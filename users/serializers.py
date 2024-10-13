from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import Role


User = get_user_model()


class CustomUserCreateSerializer(serializers.ModelSerializer):
    """
    Custom serializer for creating and updating users.

    Attributes:
        roles (PrimaryKeyRelatedField): Field for associating roles with a user.

    Meta:
        model (User): The custom user model.
        fields (tuple): List of fields to include in the serialization.
        extra_kwargs (dict): Additional options for some fields (e.g. password write-only).
    """

    roles = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all(), many=True, required=False)

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'user_phone',
                  'password', 'about_me', 'profile_picture', 'roles')
        extra_kwargs = {
            'password': {'write_only': True},
            'profile_picture': {'required': False, 'allow_null': True},
        }

    def create(self, validated_data):
        """
        Create a new user instance with validated data.

        Args:
            validated_data (dict): The validated data for creating the user.

        Returns:
            User: The created user instance.
        """
        roles_data = validated_data.pop('roles', [])
        user = User.objects.create(**validated_data)
        user.save()
        if roles_data:
            user.roles.set(roles_data)
        return user

    def update(self, instance, validated_data):
        """
        Update an existing user instance with validated data.

        Args:
            instance (User  ): The current user instance.
            validated_data (dict): The validated data for updating the user.

        Returns:
            User: The updated user instance.
        """
        if not instance.is_active:
            raise serializers.ValidationError("Inactive users cannot be updated.")

        for field, value in validated_data.items():
            if field == 'password':
                instance.set_password(value)
            elif field == 'roles':
                instance.roles.set(value)  
            else:
                setattr(instance, field, value)  

        instance.save()
        return instance
