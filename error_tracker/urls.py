from django.urls import path
from .views import ErrorLogListCreateView, ErrorGroupListView

urlpatterns = [
    path('error-logs/', ErrorLogListCreateView.as_view(), name='error-log-list-create'),
    path('error-groups/', ErrorGroupListView.as_view(), name='error-group-list'),
]
