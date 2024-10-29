import bleach
from rest_framework import serializers

from communications import init_container, CreateChatCommand, CreateMessageCommand
from communications.domain.entities.messages import Message, ChatRoom
from communications.domain.values.messages import Title

container = init_container()
create_chat_command = container.resolve(CreateChatCommand)
create_message_command = container.resolve(CreateMessageCommand)


class MessageSerializer(serializers.Serializer):
    """Serializer for representing messages in a chat"""
    sender_id = serializers.IntegerField()
    receiver_id = serializers.IntegerField()
    content = serializers.CharField(max_length=1000)
    read_at = serializers.DateTimeField(required=False, allow_null=True)

    def validate_content(self, value):
        """Custom validation for content field to check for XSS vulnerabilities."""
        if "<script>" in value or "javascript:" in value:
            raise serializers.ValidationError("Content contains potentially dangerous XSS code.")

        sanitized_content = bleach.clean(value, tags=[], attributes={}, styles=[], strip=True)

        if not sanitized_content:
            raise serializers.ValidationError("Content cannot be empty after sanitization.")

        return sanitized_content

    def create(self, validated_data):
        """Create a new Message instance from validated data and save it in MongoDB."""
        message = Message(**validated_data)
        create_message_command.handle(validated_data['room_id'], message)
        return message


class ChatRoomSerializer(serializers.Serializer):
    """Serializer for representing a chat root between
    a startup and an investor"""

    title = serializers.CharField()
    startup_id = serializers.IntegerField()
    investor_id = serializers.IntegerField()

    def create(self, validated_data):
        """Create a new ChatRoom instance and save it to MongoDB"""

        messages_data = validated_data.pop("messages", [])
        title = Title(messages_data.pop("title"))
        chat_room = ChatRoom(title=title, **validated_data)
        create_chat_command.handle(chat_room)

        return chat_room
