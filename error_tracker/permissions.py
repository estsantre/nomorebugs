# error_tracker/permissions.py
from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied
from project_integrations.models import APIKey


class HasAPIKeyPermission(BasePermission):
    """
    Custom permission to authenticate using an API key and ensure it is associated with the specified project.
    """

    def has_permission(self, request, view):
        if request.method == 'POST':
            api_key = request.headers.get('API-Key')
            project_id = request.data.get('project')

            if not api_key or not project_id:
                return False

            try:
                # Fetch the APIKey and check if it is associated with the given project
                api_key_instance = APIKey.objects.get(key=api_key, project_id=project_id)
                return True
            except APIKey.DoesNotExist:
                raise PermissionDenied("Invalid API key or project association.")

        # Allow access for GET requests or any other method
        return True
