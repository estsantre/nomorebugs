from django.db import models
from project_integrations.models import Project


class ErrorGroup(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)


class ErrorLog(models.Model):
    error_message = models.TextField()
    environment = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    error_group = models.ForeignKey(ErrorGroup, on_delete=models.CASCADE, null=True)
