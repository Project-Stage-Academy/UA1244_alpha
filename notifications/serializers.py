from rest_framework import serializers
from .models import Notification

class NotificationSerializersGet(serializers.ModelSerializer):
    """Notification Serializer for investors notifications"""
    notification_type_display = serializers.CharField(source='get_notification_type_display', read_only=True)

    class Meta:
        model = Notification
        fields = ['notification_type', 'notification_type_display', 'startup', 'created_at', 'sent_at']
        read_only_fields = ['notification_type', 'startup', 'message_id', 'created_at', 'sent_at']