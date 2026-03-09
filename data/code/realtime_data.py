import akshare as ak
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def get_live_valuation(stock_code):
    """
    Fetch live PE, PB, PEG for a company. Returns a dict.
    If fails, returns None for values.
    """
    try:
        pe_df = ak.stock_zh_valuation_baidu(symbol=stock_code, indicator="市盈率(TTM)", period="近一年")
        pb_df = ak.stock_zh_valuation_baidu(symbol=stock_code, indicator="市净率", period="近一年")
        
        pe = None
        pb = None
        peg = None
        
        if len(pe_df) > 0:
            pe = float(pe_df.iloc[-1]['value'])
        if len(pb_df) > 0:
            pb = float(pb_df.iloc[-1]['value'])
            
        # Very rough PEG estimate based on TTM PE and some static growth expectation if needed, 
        # or we could try to find peg if available. Baidu doesn't provide PEG directly.
        # We'll calculate a placeholder PEG if PE is available and positive.
        if pe is not None and pe > 0:
            peg = pe / 20.0 # Placeholder calculation or None
            
        return {"pe": pe, "pb": pb, "peg": peg}
    except Exception as e:
        logger.error(f"Error fetching live valuation for {stock_code}: {e}")
        return {"pe": None, "pb": None, "peg": None}

def get_historical_performance(stock_code):
    """
    Fetches the latest YoY growth (历史同期业绩) for a company.
    """
    try:
        df = ak.stock_financial_abstract_ths(symbol=stock_code, indicator="按报告期")
        # Columns typically include '净利润同比增长率' or something similar
        # Find column with '净利润' and '同比'
        growth_col = [c for c in df.columns if '净利润' in c and '同比' in c]
        if growth_col and len(df) > 0:
            col = growth_col[0]
            val = df.iloc[-1][col]
            if pd.notna(val) and val != '' and val is not False:
                return str(val)
    except Exception as e:
        logger.error(f"Error fetching historical performance for {stock_code}: {e}")
        
    return None

if __name__ == "__main__":
    print(get_live_valuation("002082"))
    print(get_historical_performance("002082"))
