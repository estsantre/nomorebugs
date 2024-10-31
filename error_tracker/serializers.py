from rest_framework import serializers
from .models import ErrorLog, ErrorGroup


class ErrorLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ErrorLog
        fields = ['id', 'error_message', 'environment', 'created_at', 'project', 'error_group']


class ErrorGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = ErrorGroup
        fields = ['id', 'created_at']
