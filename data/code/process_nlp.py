import os
import sys
import json
import django
import random
import re

# Add backend directory to sys.path so we can import Django models
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
sys.path.append(backend_dir)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from signal_app.models import Company, FinancialText, Signal, Valuation

def nlp_extract_signals(text_content, company=None, real_data_map=None, industry_expectations=None):
    """
    Mock NLP parser. Look for "increase_{low}%到{high}%" pattern to infer signals.
    """
    import re
    increase_match = re.search(r'(?:增长|变动|增加|增幅).*?(-?\d+)(?:%|个百分点).*?(?:到|至|-|=)(?: |-)?(-?\d+)(?:%|个百分点)', text_content)
    if increase_match:
        try:
            low = int(increase_match.group(1))
            high = int(increase_match.group(2))
            mid = (low + high) / 2
        except:
            mid = 0
    else:
        # Fallback keyword approach
        if "大幅增长" in text_content or "充沛" in text_content:
            mid = 50
        elif "疲软" in text_content or "压力" in text_content:
            mid = -10
        else:
            mid = 5
            
    # Market Expectation from real data or industry baseline
    market_expectation_pct = 15.0
    if company:
        if real_data_map and company.stock_code in real_data_map:
            market_expectation_pct = float(real_data_map[company.stock_code])
        elif industry_expectations and company.industry in industry_expectations:
            market_expectation_pct = float(industry_expectations[company.industry])
    
    # Calculate difference
    diff = mid - market_expectation_pct
    
    # Rules as per PRD
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
        
    reasoning = f"文本语义提取预测中枢增速 {mid:.2f}%，对比市场一致预期 {market_expectation_pct:.2f}%，超预期幅度为 {diff:.2f}%。"
    
    return {
        "score": score,
        "strength": strength,
        "reasoning": reasoning,
        "expected_growth": f"{mid}%",
        "market_expectation": f"{market_expectation_pct}%",
        "historical_data": f"+{random.randint(5, 20)}%"
    }

def process_scraped_data(json_file):
    print(f"Loading data from {json_file}")
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    try:
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from update_market_expectations import get_real_market_expectations, INDUSTRY_EXPECTATIONS
        real_data_map = get_real_market_expectations()
    except Exception as e:
        print("Failed to import market expectations logic:", e)
        real_data_map = None
        INDUSTRY_EXPECTATIONS = {}

    for item in data:
        # Get or create company
        company, _ = Company.objects.get_or_create(
            stock_code=item['company_code'],
            defaults={
                'name': item['company_name'],
                'industry': item['company_industry'],
                'board': item['company_board']
            }
        )
        
        # Save valuation mock
        if not hasattr(company, 'valuation'):
            Valuation.objects.create(
                company=company,
                pe=random.uniform(10, 80),
                pb=random.uniform(1, 8),
                peg=random.uniform(0.5, 2.0)
            )
        
        # Save text
        fin_text = FinancialText.objects.create(
            company=company,
            source_type=item['source_type'],
            publish_date=item['publish_date'],
            title=item['title'],
            content=item['content'],
            processed=True
        )
        
        # NLP analysis
        signal_data = nlp_extract_signals(item['content'], company, real_data_map, INDUSTRY_EXPECTATIONS)
        
        # Save signal
        Signal.objects.create(
            company=company,
            text_source=fin_text,
            score=signal_data['score'],
            strength=signal_data['strength'],
            reasoning=signal_data['reasoning'],
            expected_growth=signal_data['expected_growth'],
            market_expectation=signal_data['market_expectation'],
            historical_data=signal_data['historical_data']
        )
        
        print(f"Processed signal for {company.name}: Score {signal_data['score']} ({signal_data['strength']})")

if __name__ == "__main__":
    process_scraped_data('data.json')
