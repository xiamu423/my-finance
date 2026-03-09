import os
import sys
import django
import csv

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from signal_app.models import Company, FinancialText, Signal, Valuation

def export_companies():
    with open(r'D:\finance\data\companies.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['stock_code', 'name', 'industry', 'board'])
        for c in Company.objects.all():
            writer.writerow([c.stock_code, c.name, c.industry, c.board])
            
def export_texts():
    with open(r'D:\finance\data\financial_texts.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['company_code', 'source_type', 'publish_date', 'title', 'content', 'processed'])
        for t in FinancialText.objects.all():
            writer.writerow([t.company.stock_code, t.source_type, t.publish_date.strftime('%Y-%m-%d'), t.title, t.content, t.processed])

def export_signals():
    with open(r'D:\finance\data\signals.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['company_code', 'text_title', 'score', 'strength', 'reasoning', 'expected_growth', 'market_expectation', 'historical_data'])
        for s in Signal.objects.all():
            writer.writerow([s.company.stock_code, s.text_source.title, s.score, s.strength, s.reasoning, s.expected_growth, s.market_expectation, s.historical_data])

def export_valuations():
    with open(r'D:\finance\data\valuations.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['company_code', 'pe', 'pb', 'peg'])
        for v in Valuation.objects.all():
            writer.writerow([v.company.stock_code, v.pe, v.pb, v.peg])

if __name__ == '__main__':
    export_companies()
    export_texts()
    export_signals()
    export_valuations()
    print("Exported all CSVs successfully to D:\\finance\\data")
