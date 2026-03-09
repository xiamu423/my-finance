from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CompanyViewSet, FinancialTextViewSet, SignalViewSet, ValuationViewSet

router = DefaultRouter()
router.register(r'companies', CompanyViewSet)
router.register(r'texts', FinancialTextViewSet)
router.register(r'signals', SignalViewSet, basename='signal')
router.register(r'valuations', ValuationViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
