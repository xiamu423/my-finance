from rest_framework import serializers
from .models import Company, FinancialText, Signal, Valuation

class ValuationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Valuation
        fields = '__all__'

class CompanySerializer(serializers.ModelSerializer):
    valuation = ValuationSerializer(read_only=True)
    class Meta:
        model = Company
        fields = '__all__'

class FinancialTextSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinancialText
        fields = '__all__'

class SignalSerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only=True)
    text_source = FinancialTextSerializer(read_only=True)
    
    class Meta:
        model = Signal
        fields = '__all__'
