import os
import sys
import csv
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from signal_app.models import Company, FinancialText, Signal, Valuation

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')

def import_companies():
    print("Importing Companies...")
    path = os.path.join(DATA_DIR, 'companies.csv')
    with open(path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            try:
                Company.objects.update_or_create(
                    stock_code=row['股票代码'],
                    defaults={
                        'name': row['公司名称'],
                        'industry': row['所属行业'],
                        'board': row['上市板块']
                    }
                )
                count += 1
            except Exception as e:
                print(f"Error on {row['股票代码']}: {e}")
    print(f"Imported {count} companies.")

def import_financial_texts():
    print("Importing Financial Texts...")
    path = os.path.join(DATA_DIR, 'financial_texts.csv')
    with open(path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            try:
                company = Company.objects.get(stock_code=row['股票代码'])
                processed = True if row['已解析'].lower() == 'true' else False
                FinancialText.objects.update_or_create(
                    company=company,
                    title=row['标题'],
                    publish_date=row['发布日期'],
                    defaults={
                        'source_type': row['文本类型'],
                        'content': row['公告内容摘要'],
                        'processed': processed
                    }
                )
                count += 1
            except Company.DoesNotExist:
                print(f"Company not found for code: {row['股票代码']}")
            except Exception as e:
                print(f"Error importing text: {e}")
    print(f"Imported {count} financial texts.")

def import_signals():
    print("Importing Signals...")
    path = os.path.join(DATA_DIR, 'signals.csv')
    with open(path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            try:
                company = Company.objects.get(stock_code=row['股票代码'])
                # Try to find corresponding financial text, matching by company and date
                text_source = FinancialText.objects.filter(company=company, publish_date=row['公告发布日期']).first()
                
                Signal.objects.update_or_create(
                    company=company,
                    reasoning=row['核心依据'],
                    defaults={
                        'text_source': text_source,
                        'score': int(row['信号评分']),
                        'strength': row['信号强度'],
                        'expected_growth': row['预期增速'],
                        'market_expectation': row['市场基准'],
                    }
                )
                count += 1
            except Company.DoesNotExist:
                print(f"Company not found for code: {row['股票代码']}")
            except Exception as e:
                print(f"Error importing signal: {e}")
    print(f"Imported {count} signals.")

def import_valuations():
    print("Importing Valuations...")
    path = os.path.join(DATA_DIR, 'valuations.csv')
    with open(path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            try:
                company = Company.objects.get(stock_code=row['股票代码'])
                pe_str = str(row.get('PE市盈率', ''))
                pb_str = str(row.get('PB市净率', ''))
                peg_str = str(row.get('PEG', ''))
                
                pe = float(pe_str) if pe_str not in ['-', '', 'nan', 'None'] else None
                pb = float(pb_str) if pb_str not in ['-', '', 'nan', 'None'] else None
                peg = float(peg_str) if peg_str not in ['-', '', 'nan', 'None'] else None
                
                Valuation.objects.update_or_create(
                    company=company,
                    defaults={
                        'pe': pe,
                        'pb': pb,
                        'peg': peg,
                    }
                )
                count += 1
            except Company.DoesNotExist:
                print(f"Company not found for code: {row['股票代码']}")
            except ValueError as e:
                print(f"Value error for code: {row['股票代码']}: {e}")
            except Exception as e:
                print(f"Error importing valuation: {e}")
    print(f"Imported {count} valuations.")

if __name__ == '__main__':
    print("Starting CSV data import process...")
    import_companies()
    import_financial_texts()
    import_signals()
    import_valuations()
    print("Data import completed successfully!")
