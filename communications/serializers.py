import bleach
from rest_framework import serializers
from communications.domain.entities.messages import Message, ChatRoom
from communications.domain.values.messages import Text


class MessageSerializer(serializers.Serializer):
    """Serializer for representing messages in a chat"""
    content = serializers.CharField(max_length=1000)
    read_at = serializers.DateTimeField(required=False, allow_null=True)

    def validate_content(self, value):
        """Custom validation for content field to check for XSS vulnerabilities."""
        sanitized_content = bleach.clean(value, tags=[], attributes={}, strip=True)

        if sanitized_content != value:
            raise serializers.ValidationError(
                "Content contains unsupported characters or formatting and was sanitized."
            )

        return sanitized_content


class ChatRoomSerializer(serializers.Serializer):
    """Serializer for representing a chat root between
    a startup and an investor"""

    title = serializers.CharField()
    sender_id = serializers.IntegerField()
    receiver_id = serializers.IntegerField()

    def create(self, validated_data):
        """Create a new ChatRoom instance and save it to MongoDB"""
        mongo_chats_repo = self.context.get('mongo_chats_repo')
        if mongo_chats_repo is None:
            raise serializers.ValidationError("Database repository not provided in serializer context.")

        chat_room = ChatRoom(**validated_data)
        mongo_chats_repo.create_chatroom(chat_room)

        return chat_room
