import os
import django
import random
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from signal_app.models import Company, FinancialText, Signal, Valuation

def seed():
    print("Clearing database...")
    Company.objects.all().delete()
    
    industries = ['计算机', '电子', '医药', '新能源', '金融']
    boards = ['主板', '创业板', '科创板']
    
    print("Creating companies and valuations...")
    companies = []
    for i in range(10):
        c = Company.objects.create(
            stock_code=f"{random.randint(0, 999999):06d}",
            name=f"测试公司_{i+1}",
            industry=random.choice(industries),
            board=random.choice(boards)
        )
        Valuation.objects.create(
            company=c,
            pe=random.uniform(10, 100),
            pb=random.uniform(1, 10),
            peg=random.uniform(0.5, 3.0)
        )
        companies.append(c)
        
    print("Creating texts and signals...")
    for c in companies:
        text = FinancialText.objects.create(
            company=c,
            source_type='announcement',
            publish_date=timezone.now().date(),
            title=f"{c.name} 2026年半年度业绩预告",
            content=f"{c.name}预计2026年半年度实现归属于上市公司股东的净利润为10亿元到12亿元，同比增加50%到80%。主要原因是订单量大幅增长，产能利用率提升。",
            processed=True
        )
        
        score = random.randint(30, 100)
        if score > 80:
            strength = 'strong'
        elif score > 60:
            strength = 'medium'
        elif score > 50:
            strength = 'weak'
        else:
            strength = 'negative'
            
        Signal.objects.create(
            company=c,
            text_source=text,
            score=score,
            strength=strength,
            reasoning="净利润预计同比增加50%-80%，超市场一致预期15%。",
            expected_growth="+50% ~ +80%",
            market_expectation="+35%",
            historical_data="+20%"
        )

    print("Seed complete! Created 10 companies + associated data.")

if __name__ == "__main__":
    seed()
