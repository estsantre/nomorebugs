from django.urls import path
from .views import APIKeyCreateView, ProjectListCreateView, ProjectRetrieveUpdateDestroyView

urlpatterns = [
    path('projects/', ProjectListCreateView.as_view(), name='project_list_create'),
    path('projects/<int:pk>/', ProjectRetrieveUpdateDestroyView.as_view(), name='project_detail'),
    path('api-key/create/', APIKeyCreateView.as_view(), name='api_key_create'),
]
