from rest_framework import serializers
from .models import APIKey, Project


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['name', 'created_at', 'id', 'uuid']
        read_only_fields = ['created_at', 'id', 'uuid']

    def create(self, validated_data):
        # Automatically assign the user to the project
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class APIKeyCreateSerializer(serializers.ModelSerializer):
    project = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=Project.objects.all(),
        write_only=True
    )
    key = serializers.UUIDField(read_only=True)

    class Meta:
        model = APIKey
        fields = ['key', 'project', 'id']

    def create(self, validated_data):
        # Ensure the API key is linked to the user who owns the project
        project = validated_data['project']
        user = self.context['request'].user

        if project.user != user:
            raise serializers.ValidationError("You do not own this project.")

        # Create and return the new API key
        return APIKey.objects.create(user=user, project=project)


class APIKeyReadOnlySerializer(serializers.ModelSerializer):
    project = serializers.StringRelatedField()
    project_uuid = serializers.UUIDField(source='project.uuid', read_only=True)

    class Meta:
        model = APIKey
        fields = ['id', 'project', 'created_at', 'project_uuid']