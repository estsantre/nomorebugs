from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, generics
from .serializers import APIKeyCreateSerializer, ProjectSerializer
from .models import Project


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
            return Response({'key': api_key.key}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
