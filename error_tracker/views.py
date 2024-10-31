# error_tracker/views.py
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import ErrorLog, ErrorGroup
from .serializers import ErrorLogSerializer, ErrorGroupSerializer
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


class ErrorGroupListView(generics.ListAPIView):
    """
    Handles GET requests for listing ErrorGroups with JWT authentication.
    """
    queryset = ErrorGroup.objects.all()
    serializer_class = ErrorGroupSerializer
    permission_classes = [IsAuthenticated]
