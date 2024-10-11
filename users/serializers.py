from django.contrib.auth import get_user_model
from rest_framework import serializers
from djoser.serializers import UserCreateSerializer
from .models import Role


User = get_user_model()


class CustomUserCreateSerializer(UserCreateSerializer):
    roles = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all(), many=True, required=False)

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ('email', 'first_name', 'last_name', 'user_phone',
                  'password', 'about_me', 'profile_picture', 'roles')
        extra_kwargs = {
            'password': {'write_only': True},
            'profile_picture': {'required': False, 'allow_null': True},
        }

    def create(self, validated_data):
        roles_data = validated_data.pop('roles', [])
        user = User.objects.create(**validated_data)
        user.save()
        if roles_data:
            user.roles.set(roles_data)

        return user
