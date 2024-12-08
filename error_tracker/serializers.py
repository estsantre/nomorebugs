from rest_framework import serializers
from .models import ErrorLog, Project


class ErrorLogSerializer(serializers.ModelSerializer):
    project = serializers.UUIDField(format='hex_verbose', required=True)  # Accept UUID as input

    class Meta:
        model = ErrorLog
        fields = ['id', 'error_message', 'environment', 'created_at', 'project']

    def validate_project(self, value):
        """
        This method will convert the UUID string to a Project instance.
        """
        try:
            return Project.objects.get(uuid=value)
        except Project.DoesNotExist:
            raise serializers.ValidationError("Project with this UUID does not exist.")
