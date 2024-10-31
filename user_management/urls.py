from django.urls import path
from .views import UserProfileDetailView, CustomTokenObtainPairView, CustomTokenRefreshView, LogoutView

urlpatterns = [
    path('profile/', UserProfileDetailView.as_view(), name='user-profile'),
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
]