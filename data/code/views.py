from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from datetime import timedelta
from rest_framework.response import Response
from .models import Company, FinancialText, Signal, Valuation
from .serializers import CompanySerializer, FinancialTextSerializer, SignalSerializer, ValuationSerializer
from .realtime_data import get_live_valuation, get_historical_performance

STRENGTH_ORDER = {'strong': 0, 'medium': 1, 'weak': 2, 'negative': 3}

class CompanyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['industry', 'board']
    search_fields = ['stock_code', 'name']

class FinancialTextViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FinancialText.objects.all()
    serializer_class = FinancialTextSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['company', 'source_type', 'processed']

class SignalViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SignalSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['strength']

    def get_queryset(self):
        cutoff = timezone.now().date() - timedelta(days=30)
        return (
            Signal.objects
            .select_related('company', 'text_source')
            .filter(text_source__publish_date__gte=cutoff)
            .order_by('-text_source__publish_date', '-score')
        )
        
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data
        
        # Inject live data
        stock_code = instance.company.stock_code
        live_val = get_live_valuation(stock_code)
        hist_perf = get_historical_performance(stock_code)
        
        if live_val['pe'] is not None:
            # Overwrite the nested valuation
            data['company']['valuation'] = {
                'pe': live_val['pe'],
                'pb': live_val['pb'],
                'peg': live_val['peg'] if live_val['peg'] is not None else (instance.company.valuation.peg if hasattr(instance.company, 'valuation') else 1.0)
            }
            
        if hist_perf:
            # Akshare THS returns string value typically already ending with %
            if not hist_perf.endswith('%'):
                hist_perf += '%'
            data['historical_data'] = hist_perf
        else:
            data['historical_data'] = None
            
        return Response(data)

class ValuationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Valuation.objects.all()
    serializer_class = ValuationSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['company']
