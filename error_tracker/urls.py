from django.urls import path
from .views import ErrorLogListCreateView

urlpatterns = [
    path('error-logs/', ErrorLogListCreateView.as_view(), name='error-log-list-create'),
]
