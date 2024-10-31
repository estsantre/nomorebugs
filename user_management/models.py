from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    """
    Extends the Django User model with additional fields.
    """

    USER_TYPE_CHOICES = [
        ('free', 'Free'),
        ('premium', 'Premium'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    account_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='free')

    def __str__(self):
        return self.user.username