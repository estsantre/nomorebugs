from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User


class UserProfileTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.user.profile.account_type = 'premium'
        self.user.profile.save()
        self.client.force_authenticate(user=self.user)

    def test_user_profile_retrieval(self):
        response = self.client.get(reverse('user-profile'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['account_type'], 'premium')

    def test_user_profile_update(self):
        data = {'account_type': 'free'}
        response = self.client.put(reverse('user-profile'), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.account_type, 'free')


class AuthTokenTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')

    def test_login_valid_credentials(self):
        url = reverse('token_obtain_pair')
        data = {'username': 'testuser', 'password': 'password'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_invalid_credentials(self):
        url = reverse('token_obtain_pair')
        data = {'username': 'testuser', 'password': 'wrongpassword'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_refresh(self):
        refresh = RefreshToken.for_user(self.user)
        url = reverse('token_refresh')
        data = {'refresh': str(refresh)}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_token_refresh_invalid(self):
        url = reverse('token_refresh')
        data = {'refresh': 'invalidtoken'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_token_blacklisted_after_refresh(self):
        refresh = RefreshToken.for_user(self.user)
        url = reverse('token_refresh')
        data = {'refresh': str(refresh)}
        self.client.post(url, data, format='json')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class LogoutTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        refresh = RefreshToken.for_user(self.user)
        self.refresh_token = str(refresh)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        self.logout_url = reverse('logout')

    def test_logout_valid_refresh_token(self):
        response = self.client.post(self.logout_url, {'refresh_token': self.refresh_token}, format='json')
        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)

    def test_logout_no_refresh_token(self):
        response = self.client.post(self.logout_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_token_is_blacklisted_after_logout(self):
        self.client.post(self.logout_url, {'refresh_token': self.refresh_token}, format='json')
        response = self.client.post(reverse('token_refresh'), {'refresh': self.refresh_token}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
