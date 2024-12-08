from django.urls import path
from .views import (APIKeyCreateView, ProjectListCreateView, ProjectRetrieveUpdateDestroyView, APIKeyListView,
                    APIKeyDeleteView)

urlpatterns = [
    path('projects/', ProjectListCreateView.as_view(), name='project_list_create'),
    path('projects/<int:pk>/', ProjectRetrieveUpdateDestroyView.as_view(), name='project_detail'),
    path('api-keys/create/', APIKeyCreateView.as_view(), name='api_key_create'),
    path('api-keys/', APIKeyListView.as_view(), name='api_key_list'),
    path('api-keys/<int:api_key_id>/', APIKeyDeleteView.as_view(), name='api_key_delete'),

]
