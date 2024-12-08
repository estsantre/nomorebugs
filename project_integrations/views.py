from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, generics
from .serializers import ProjectSerializer, APIKeyCreateSerializer, APIKeyReadOnlySerializer
from .models import Project, APIKey


# List/Create Projects
class ProjectListCreateView(generics.ListCreateAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Restrict to projects owned by the authenticated user
        return Project.objects.filter(user=self.request.user)


# Retrieve/Update/Delete a Single Project
class ProjectRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Restrict to projects owned by the authenticated user
        return Project.objects.filter(user=self.request.user)


class APIKeyCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = APIKeyCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            api_key = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class APIKeyListView(generics.ListAPIView):
    serializer_class = APIKeyReadOnlySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Ensure only the API keys of the authenticated user are returned
        return APIKey.objects.filter(user=self.request.user)


class APIKeyDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, api_key_id):
        try:
            # Retrieve the API key object owned by the user
            api_key = APIKey.objects.get(id=api_key_id, user=request.user)
            api_key.delete()
            return Response({"detail": "API key deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except APIKey.DoesNotExist:
            return Response({"detail": "API key not found."}, status=status.HTTP_404_NOT_FOUND)
