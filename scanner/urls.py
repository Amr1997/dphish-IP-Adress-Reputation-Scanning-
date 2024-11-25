from django.urls import path
from .views import IPScanView, WebhookView

urlpatterns = [
    path('scan/', IPScanView.as_view(), name='ip_scan'),  
    path('webhook/', WebhookView.as_view(), name='webhook'), 
]
