from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Role, User
from django.db import transaction


User = get_user_model()


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ('id', 'name')


class CustomUserCreateSerializer(serializers.ModelSerializer):
    """
    Custom serializer for creating and updating users.

    Attributes:
        roles (PrimaryKeyRelatedField): Field for associating roles with a user.
    """
    roles = serializers.PrimaryKeyRelatedField(
        queryset=Role.objects.all(), many=True, required=False
    )
    profile_picture = serializers.ImageField(
        required=False, allow_null=True
    )

    class Meta:
        model = User
        fields = (
            'email', 'first_name', 'last_name', 'user_phone',
            'password', 'about_me', 'profile_picture', 'roles'
        )
        extra_kwargs = {
            'password': {'write_only': True},
            'profile_picture': {'required': False, 'allow_null': True},
        }

    def set_roles_and_password(self, instance, validated_data):
        """Set the user's password and roles if provided."""
        if 'password' in validated_data:
            instance.set_password(validated_data['password'])
        if 'roles' in validated_data:
            instance.roles.set(validated_data['roles'])

    @transaction.atomic
    def create(self, validated_data):
        """Create a new user instance with validated data."""
        user = User.objects.create(**validated_data)
        self.set_roles_and_password(user, validated_data)
        user.save()
        return user

    @transaction.atomic
    def update(self, instance, validated_data):
        """Update an existing user instance."""
        if not instance.is_active:
            raise serializers.ValidationError(
                "Inactive users cannot be updated."
            )

        for field, value in validated_data.items():
            if field not in {'password', 'roles'}:
                setattr(instance, field, value)

        self.set_roles_and_password(instance, validated_data)
        instance.save()
        return instance


class UserSerializer(serializers.ModelSerializer):
    roles = serializers.StringRelatedField(many=True)

    class Meta:
        model = User
        fields = (
            'id', 'email', 'first_name', 'last_name',
            'roles', 'about_me', 'profile_picture', 'is_active',
            'last_login', 'created_at', 'updated_at', 'is_soft_deleted'
        )
        read_only_fields = ('is_active',)
        ref_name = 'User_'

    def to_representation(self, instance):
        """Control the visibility of fields depending on the user's role"""
        data = super().to_representation(instance)

        if not self.context['request'].user.is_staff:
            for field in [
                'is_active', 'last_login', 'created_at',
                'updated_at', 'is_soft_deleted'
            ]:
                data.pop(field, None)

        return data




