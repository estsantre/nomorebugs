import re
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import ErrorLog
from .serializers import ErrorLogSerializer
from .permissions import HasAPIKeyPermission


class ErrorLogListCreateView(generics.ListCreateAPIView):
    """
    Handles GET requests for listing ErrorLogs with JWT authentication.
    Handles POST requests for creating ErrorLogs with APIKey authentication.
    """
    queryset = ErrorLog.objects.all()
    serializer_class = ErrorLogSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [HasAPIKeyPermission()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):

        error_data = self.request.data.get("error_message", "")

        # Extract error type and key details from the message
        # error_type, error_signature = self._extract_error_details(error_data)
        #
        # # Find or create an ErrorGroup for this error type and signature
        # error_group, created = ErrorGroup.objects.get_or_create(
        #     error_type=error_type,
        #     error_signature=error_signature
        # )

        # Save the ErrorLog with the associated ErrorGroup
        # serializer.save(error_group=error_group)
        serializer.save()

    def _extract_error_details(self, error_message):
        """
        Helper method to extract the error type and a signature from the error message.
        """
        # Basic regex to capture the error type (e.g., TypeError) and location
        type_match = re.search(r'(\w+Error):', error_message)
        location_match = re.search(r'File "(.+)", line (\d+)', error_message)

        error_type = type_match.group(1) if type_match else "UnknownError"
        error_signature = f"{location_match.group(1)}:{location_match.group(2)}" if location_match else "unknown_location"

        return error_type, error_signature
