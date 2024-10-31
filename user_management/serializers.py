from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the Django User model.
    """

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for the UserProfile model.
    """
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = ['user', 'account_type']

    def update(self, instance, validated_data):
        # Allow partial updates of the profile
        account_type = validated_data.get('account_type', instance.account_type)

        instance.account_type = account_type
        instance.save()

        return instance
