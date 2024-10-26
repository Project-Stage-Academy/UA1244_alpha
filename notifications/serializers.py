from rest_framework import serializers
from .models import Notification

class NotificationSerializersGet(serializers.ModelSerializer):

    class Meta:
        model = Notification
        fields = ['notification_type', 'startup', 'message_id', 'created_at']