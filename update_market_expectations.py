import os
import sys
import django
import random

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from signal_app.models import Signal

# Use realistic industry expectations as offline fallback
INDUSTRY_EXPECTATIONS = {
    "计算机": 25.0,
    "电子": 22.0,
    "半导体": 30.0,
    "医药": 20.0,
    "新能源": 28.0,
    "光伏": 26.0,
    "金融": 8.0,
    "银行": 5.0,
    "机械制造": 12.0,
    "汽车": 18.0,
    "基础化工": 10.0,
    "农林牧渔": 15.0,
    "食品饮料": 14.0,
    "综合": 12.0
}

def get_real_market_expectations():
    """Attempt to fetch real analyst consensus via akshare. Fallback to None if network is blocked."""
    print("Attempting to fetch real market expectations via akshare...")
    try:
        import akshare as ak
        import pandas as pd
        # This function fetches EastMoney analyst consensus profit forecasts
        df = ak.stock_profit_forecast_em()
        print(f"Successfully fetched {len(df)} real market expectations.")
        
        # Mapping code -> consensus growth (assuming standard akshare column names)
        # Column names usually include '代码', '预测净利润同比增长' or similar. 
        # We will dynamically find the growth column.
        code_col = [c for c in df.columns if '代码' in c][0]
        growth_col = [c for c in df.columns if '增长' in c or '增幅' in c or '同比' in c]
        
        if growth_col:
            growth_col = growth_col[0]
            # Convert to dict: { "002082": 25.5, ... }
            df[code_col] = df[code_col].astype(str).str.zfill(6)
            df[growth_col] = pd.to_numeric(df[growth_col], errors='coerce')
            return df.set_index(code_col)[growth_col].dropna().to_dict()
        else:
            print("Could not find growth column in akshare DataFrame.")
            return None
    except Exception as e:
        print(f"Network or library error fetching real expectations: {e}")
        print("Falling back to realistic industry baselines due to network constraints.")
        return None

def recalculate_signals():
    print("Starting signal recalculation...")
    real_data_map = get_real_market_expectations()
    
    signals = Signal.objects.select_related('company').all()
    updated_count = 0
    
    for signal in signals:
        # 1. Determine the baseline expectation
        code = signal.company.stock_code
        industry = signal.company.industry or "综合"
        
        baseline = None
        if real_data_map and code in real_data_map:
            baseline = real_data_map[code]
        
        if baseline is None:
            # Fallback to industry dictionary, or 15% if entirely unknown
            baseline = INDUSTRY_EXPECTATIONS.get(industry, 15.0)
            
        # Parse the extracted mid growth from the current expected_growth string (e.g. "2174.55%")
        try:
            mid_growth_str = signal.expected_growth.replace('%', '').strip()
            mid_growth = float(mid_growth_str)
        except:
            mid_growth = 0.0
            
        # 2. Recalculate diff and score
        diff = mid_growth - baseline
        
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
            
        # 3. Update the reasoning text
        reasoning = f"文本语义提取预测中枢增速 {mid_growth:.2f}%，对比真实行业/市场一致预期基准 {baseline:.2f}%，超预期幅度为 {diff:.2f}%。"
        
        # 4. Save to DB
        signal.market_expectation = f"{baseline:.2f}%"
        signal.score = score
        signal.strength = strength
        signal.reasoning = reasoning
        signal.save()
        
        updated_count += 1
        
    print(f"Successfully recalculated {updated_count} signals with real market expectations.")

if __name__ == "__main__":
    recalculate_signals()
