from django.forms import ValidationError
from rest_framework import serializers

from users.models import Role
from users.serializers import RoleSerializer

from .models import Notification, NotificationPreferences, RolesNotifications, NotificationType


class NotificationSerializer(serializers.ModelSerializer):
    """Notification Serializer"""
    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = [
            'notification_type',
            'investor',
            'startup',
            'message_id',
            'delivery_status',
            'created_at',
            'sent_at',
            'read_at'
        ]


class ExtendedNotificationSerializer(serializers.ModelSerializer):
    """Notification Serializer"""
    associated_profile_url = serializers.SerializerMethodField()
    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = [
            'notification_type',
            'investor',
            'startup',
            'message_id',
            'delivery_status',
            'created_at',
            'sent_at',
            'read_at'
        ]
    
    def get_associated_profile_url(self, obj):
        return obj.get_associated_profile_url()


class NotificationPreferencesSerializer(serializers.ModelSerializer):
    """Notification Preferences model Serializer"""
    class Meta:
        model = NotificationPreferences
        fields = '__all__'
        read_only_fields = ['user', 'role', 'notification_type']


class RolesNotificationsSerializer(serializers.ModelSerializer):
    """Roles Notifications model Serializer"""

    role_name = serializers.SerializerMethodField()
    notification_name = serializers.SerializerMethodField()
    class Meta:
        model = RolesNotifications
        fields = ['id', 'role', 'notification_type', 'role_name', 'notification_name']

    def get_role_name(self, obj):
        """get role name"""
        try:
            return obj.role.name
        except obj.role.DoesNotExist:
            return None
        
    def get_notification_name(self, obj):
        """get notification type name"""
        try:
            return NotificationType(obj.notification_type).label
        except Exception:
            return None

