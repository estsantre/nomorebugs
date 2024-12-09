from django.urls import path
from .views import AnalyzeBugView

urlpatterns = [
    path('error-log/<int:errorLogId>/', AnalyzeBugView.as_view(), name='analyze_error_log')
]
