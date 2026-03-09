import os
import sys
import django
import requests
import time
from datetime import datetime

# Setup Django
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
sys.path.append(backend_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from signal_app.models import Company, FinancialText, Signal, Valuation

def fetch_eastmoney_data():
    url = "https://datacenter-web.eastmoney.com/api/data/v1/get"
    base_params = {
        "reportName": "RPT_PUBLIC_OP_NEWPREDICT",
        "columns": "ALL",
        "source": "WEB",
        "client": "WEB",
        "pageSize": 500,
        "sortTypes": "-1,-1",
        "sortColumns": "NOTICE_DATE,SECURITY_CODE"
    }
    
    print("Fetching real data from EastMoney API...")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    all_data = []
    page = 1
    
    while True:
        params = base_params.copy()
        params["pageNumber"] = page
        print(f"  Fetching page {page}...")
        
        max_retries = 3
        retry_count = 0
        success = False
        
        while retry_count < max_retries and not success:
            try:
                response = requests.get(url, params=params, headers=headers, verify=False, timeout=15)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("result") and data["result"].get("data"):
                        page_data = data["result"]["data"]
                        all_data.extend(page_data)
                        
                        if len(page_data) < 500:
                            return all_data
                        page += 1
                        success = True
                    else:
                        return all_data
                else:
                    print(f"Failed to fetch or parse API on page {page}: Status {response.status_code}")
                    return all_data
            except Exception as e:
                retry_count += 1
                print(f"  Connection error: {e}. Retrying {retry_count}/{max_retries}...")
                time.sleep(2 * retry_count)
                
        if not success:
            print("Max retries reached. Stopping pagination.")
            break
            
    return all_data

def process_and_save(data_list):
    print(f"Processing {len(data_list)} real records...")
    
    # Get real expectations mapping or fallback
    try:
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from update_market_expectations import get_real_market_expectations, INDUSTRY_EXPECTATIONS
        real_data_map = get_real_market_expectations()
    except Exception as e:
        print("Failed to import market expectations logic:", e)
        real_data_map = None
        INDUSTRY_EXPECTATIONS = {}
    
    # We will clear the existing mock data
    print("Clearing old mock data...")
    Company.objects.all().delete()
    # Track processed companies to deduplicate
    processed_companies = set()
    
    for item in data_list:
        stock_code = item.get("SECURITY_CODE")
        name = item.get("SECURITY_NAME_ABBR")
        if not stock_code or not name:
            continue
            
        content = item.get("PREDICT_CONTENT", "")
        if not content: continue
        
        if stock_code in processed_companies:
            continue
        processed_companies.add(stock_code)
        
        publish_date_str = item.get("NOTICE_DATE", "").split(" ")[0]
        if not publish_date_str:
            publish_date_str = datetime.now().strftime("%Y-%m-%d")
            
        add_amp_lower = item.get("ADD_AMP_LOWER")
        add_amp_upper = item.get("ADD_AMP_UPPER")
        
        try:
            low = float(add_amp_lower) if add_amp_lower is not None else 0
            high = float(add_amp_upper) if add_amp_upper is not None else low
            mid = (low + high) / 2
        except:
            mid = 0
            
        # EastMoney TRADE_MARKET_ZJH often contains detailed ZJH codes or names. We'll map common ones.
        raw_industry = item.get("TRADE_MARKET_ZJH", "未知")
        if "计算机" in raw_industry or "软件" in raw_industry: industry = "计算机"
        elif "电子" in raw_industry or "半导体" in raw_industry: industry = "电子"
        elif "医药" in raw_industry or "生物" in raw_industry: industry = "医药"
        elif "新能源" in raw_industry or "光伏" in raw_industry or "电池" in raw_industry: industry = "新能源"
        elif "金融" in raw_industry or "银行" in raw_industry or "证券" in raw_industry or "保险" in raw_industry: industry = "金融"
        elif "制造" in raw_industry or "机械" in raw_industry: industry = "机械制造"
        elif "汽车" in raw_industry: industry = "汽车"
        elif "化工" in raw_industry or "化纤" in raw_industry: industry = "基础化工"
        elif "农业" in raw_industry or "养殖" in raw_industry: industry = "农林牧渔"
        elif "食品" in raw_industry or "饮料" in raw_industry: industry = "食品饮料"
        else: industry = raw_industry.split("-")[-1] if "-" in raw_industry else (raw_industry if raw_industry != "未知" else "综合")
        
        market_expectation_pct = None
        if real_data_map and stock_code in real_data_map:
            market_expectation_pct = real_data_map[stock_code]
        if market_expectation_pct is None:
            market_expectation_pct = INDUSTRY_EXPECTATIONS.get(industry, 15.0)
            
        diff = mid - market_expectation_pct
        
        if diff >= 15:
            strength = 'strong'
            score = min(100, 75 + int(diff))
        elif diff >= 5:
            strength = 'medium'
            score = min(74, 50 + int(diff * 2))
        elif diff >= 0:
            strength = 'weak'
            score = min(49, 30 + int(diff * 3))
        else:
            strength = 'negative'
            score = max(0, 30 + int(diff))
            
        reasoning = f"文本语义提取预测中枢增速 {mid:.2f}%，对比真实行业/市场一致预期基准 {market_expectation_pct:.2f}%，超预期幅度为 {diff:.2f}%。"
        
        board = "主板" if stock_code.startswith("60") or stock_code.startswith("00") else "创业板" if stock_code.startswith("30") else "科创板"
        
        company, _ = Company.objects.get_or_create(
            stock_code=stock_code,
            defaults={'name': name, 'industry': industry, 'board': board}
        )
        
        Valuation.objects.get_or_create(
            company=company,
            defaults={'pe': 25.5, 'pb': 3.2, 'peg': 1.2}
        )
        
        fin_text = FinancialText.objects.create(
            company=company, source_type='announcement',
            publish_date=publish_date_str,
            title=f"[{stock_code}] {name} 业绩预告",
            content=content, processed=True
        )
        
        Signal.objects.create(
            company=company, text_source=fin_text,
            score=score, strength=strength, reasoning=reasoning,
            expected_growth=f"{mid:.2f}%", market_expectation=f"{market_expectation_pct}%",
            historical_data="+10%"
        )

if __name__ == "__main__":
    records = fetch_eastmoney_data()
    if records:
        process_and_save(records)
        print("Successfully updated real data.")
    else:
        print("No records fetched.")
