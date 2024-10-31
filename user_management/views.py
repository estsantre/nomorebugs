from rest_framework import generics
from .models import UserProfile
from .serializers import UserProfileSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status


class UserProfileDetailView(generics.RetrieveUpdateAPIView):
    """
    View to retrieve and update the user profile.
    """
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Return the profile of the logged-in user
        return self.request.user.profile


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    This view handles user login and returns JWT access and refresh tokens.
    """
    pass


class CustomTokenRefreshView(TokenRefreshView):
    """
    This view handles token refresh, allowing the user to get a new access token
    by providing a valid refresh token.
    """
    pass


class LogoutView(APIView):
    """
    This view handles user logout by blacklisting the refresh token,
    so it can't be used anymore.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data['refresh_token']
            token = RefreshToken(refresh_token)
            token.blacklist()  # Blacklist the refresh token
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)