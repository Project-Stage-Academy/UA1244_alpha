import logging
from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Role, User
from django.db import transaction

logger = logging.getLogger('users')

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'email'

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if not email or not password:
            raise serializers.ValidationError(
                'Must include "email" and "password".'
            )

        user = authenticate(
            request=self.context.get('request'),
            email=email,
            password=password
        )

        if not user:
            raise serializers.ValidationError(
                'No active account found with the given credentials'
            )

        if not user.is_active:
            raise serializers.ValidationError('Account is disabled.')

        refresh = self.get_token(user)

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.id,
                'email': user.email,
                'roles': [role.name for role in user.roles.all()]
            }
        }


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ('id', 'name')


class CustomUserCreateSerializer(serializers.ModelSerializer):
    """
    Custom serializer for creating and updating users.
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
        logger.debug(f"Setting roles and password for user: {instance.email}")

        try:
            if 'password' in validated_data:
                instance.set_password(validated_data['password'])
                logger.debug(f"Password updated for user: {instance.email}")

            if 'roles' in validated_data:
                instance.roles.set(validated_data['roles'])
                role_names = [role.name for role in validated_data['roles']]
                logger.info(
                    "Roles updated for user",
                    extra={
                        'user_email': instance.email,
                        'roles': role_names
                    }
                )
        except Exception as e:
            logger.error(
                "Error setting roles and password",
                extra={
                    'user_email': instance.email,
                    'error': str(e)
                }
            )
            raise

    @transaction.atomic
    def create(self, validated_data):
        """Create a new user instance with validated data."""
        logger.debug(f"Attempting to create user with email: {validated_data.get('email')}")

        try:
            user = User.objects.create(**validated_data)
            self.set_roles_and_password(user, validated_data)
            user.save()

            logger.info(
                "Successfully created new user",
                extra={
                    'user_email': user.email,
                    'roles': [role.name for role in user.roles.all()]
                }
            )
            return user

        except Exception as e:
            logger.error(
                "Failed to create user",
                extra={
                    'email': validated_data.get('email'),
                    'error': str(e)
                }
            )
            raise

    @transaction.atomic
    def update(self, instance, validated_data):
        """Update an existing user instance."""
        logger.debug(f"Attempting to update user: {instance.email}")

        try:
            if not instance.is_active:
                logger.warning(
                    "Attempt to update inactive user",
                    extra={'user_email': instance.email}
                )
                raise serializers.ValidationError(
                    "Inactive users cannot be updated."
                )

            for field, value in validated_data.items():
                if field not in {'password', 'roles'}:
                    setattr(instance, field, value)

            self.set_roles_and_password(instance, validated_data)
            instance.save()

            logger.info(
                "Successfully updated user",
                extra={
                    'user_email': instance.email,
                    'updated_fields': list(validated_data.keys())
                }
            )
            return instance

        except Exception as e:
            logger.error(
                "Failed to update user",
                extra={
                    'user_email': instance.email,
                    'error': str(e)
                }
            )
            raise


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
        logger.debug(f"Serializing user data for: {instance.email}")

        try:
            data = super().to_representation(instance)

            if not self.context['request'].user.is_staff:
                restricted_fields = [
                    'is_active', 'last_login', 'created_at',
                    'updated_at', 'is_soft_deleted'
                ]
                for field in restricted_fields:
                    data.pop(field, None)
                logger.debug(
                    "Restricted fields removed for non-staff user",
                    extra={'user_email': instance.email}
                )
            data['roles'] = [role.name for role in instance.roles.all()]

            logger.info(
                "Successfully serialized user data",
                extra={'user_email': instance.email}
            )
            return data

        except Exception as e:
            logger.error(
                "Failed to serialize user data",
                extra={
                    'user_email': instance.email,
                    'error': str(e)
                }
            )
            raise


