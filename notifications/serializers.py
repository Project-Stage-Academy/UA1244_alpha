from rest_framework import serializers
from .models import Notification

class NotificationForInvestorSerializersList(serializers.ModelSerializer):
    """Notification Serializer for investors notifications"""
    notification_type_display = serializers.CharField(source='get_notification_type_display', read_only=True)

    class Meta:
        model = Notification
        fields = ['notification_type', 'notification_type_display', 'startup', 'created_at', 'sent_at']
        read_only_fields = ['notification_type', 'startup', 'message_id', 'created_at', 'sent_at']

        
class NotificationSerializer(serializers.ModelSerializer):
    """Notification Serializer"""
    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = [
            'notification_type',
            'investor',
            'startup',
            'project',
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
            'project',
            'message_id',
            'delivery_status',
            'created_at',
            'sent_at',
            'read_at'
        ]
    
    def get_associated_profile_url(self, obj):
        return obj.get_associated_profile_url()
