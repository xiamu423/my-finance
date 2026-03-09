from django.db import models

class Company(models.Model):
    stock_code = models.CharField(max_length=10, unique=True, verbose_name="股票代码")
    name = models.CharField(max_length=100, verbose_name="公司名称")
    industry = models.CharField(max_length=100, verbose_name="所属行业", blank=True, null=True)
    board = models.CharField(max_length=50, verbose_name="上市板块", blank=True, null=True)

    def __str__(self):
        return f"{self.stock_code} - {self.name}"

class FinancialText(models.Model):
    TEXT_SOURCE_CHOICES = [
        ('announcement', '业绩预告/快报'),
        ('minutes', '交流会纪要'),
        ('other', '其他')
    ]
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='texts')
    source_type = models.CharField(max_length=20, choices=TEXT_SOURCE_CHOICES, verbose_name="文本来源类型")
    publish_date = models.DateField(verbose_name="发布日期")
    title = models.CharField(max_length=200, verbose_name="标题")
    content = models.TextField(verbose_name="文本原文")
    processed = models.BooleanField(default=False, verbose_name="是否已解析")

    def __str__(self):
        return f"{self.company.name} - {self.title} ({self.publish_date})"

class Signal(models.Model):
    STRENGTH_CHOICES = [
        ('strong', '强信号'),
        ('medium', '中信号'),
        ('weak', '弱信号'),
        ('negative', '无信号/负面信号'),
    ]
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='signals')
    text_source = models.ForeignKey(FinancialText, on_delete=models.SET_NULL, null=True, blank=True, related_name='generated_signals')
    generate_time = models.DateTimeField(auto_now_add=True, verbose_name="生成时间")
    score = models.IntegerField(verbose_name="超预期信号评分 (0-100)")
    strength = models.CharField(max_length=20, choices=STRENGTH_CHOICES, verbose_name="信号强度")
    reasoning = models.TextField(verbose_name="核心支撑依据")
    expected_growth = models.CharField(max_length=100, verbose_name="预期业绩增速/区间", blank=True, null=True)
    
    # 对比基准快照
    market_expectation = models.CharField(max_length=100, verbose_name="市场一致预期快照", blank=True, null=True)
    historical_data = models.CharField(max_length=100, verbose_name="历史同期业绩快照", blank=True, null=True)

    def __str__(self):
        return f"[{self.strength}] {self.company.name} - Score: {self.score}"

class Valuation(models.Model):
    company = models.OneToOneField(Company, on_delete=models.CASCADE, related_name='valuation')
    pe = models.FloatField(verbose_name="市盈率(PE)", null=True, blank=True)
    pb = models.FloatField(verbose_name="市净率(PB)", null=True, blank=True)
    peg = models.FloatField(verbose_name="PEG", null=True, blank=True)
    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name} Valuation"
