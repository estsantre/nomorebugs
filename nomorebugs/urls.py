from django.contrib import admin
from django.urls import include
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('user_management.urls')),
    path('api/project-integrations/', include('project_integrations.urls')),
    path('api/error-tracker/', include('error_tracker.urls')),

]
