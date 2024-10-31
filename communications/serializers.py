import bleach
from rest_framework import serializers
from communications import init_container, MongoDBRepository
from communications.entities.messages import Message, ChatRoom

container = init_container()
mongo_container = container.resolve(MongoDBRepository)


class MessageSerializer(serializers.Serializer):
    """Serializer for representing messages in a chat"""
    sender_id = serializers.IntegerField()
    receiver_id = serializers.IntegerField()
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

    def create(self, validated_data):
        """Create a new Message instance from validated data and save it in MongoDB."""
        mongo_repo = self.context.get('mongo_repo')
        room_id = self.context.get('room_id')
        if mongo_repo is None:
            raise serializers.ValidationError("Database repository not provided in serializer context.")

        message = Message(**validated_data)
        mongo_repo.add_message(room_id, message)

        return message


class ChatRoomSerializer(serializers.Serializer):
    """Serializer for representing a chat root between
    a startup and an investor"""

    room_id = serializers.CharField()
    startup_id = serializers.IntegerField()
    investor_id = serializers.IntegerField()

    def create(self, validated_data):
        """Create a new ChatRoom instance and save it to MongoDB"""
        mongo_repo = self.context.get('mongo_repo')
        if mongo_repo is None:
            raise serializers.ValidationError("Database repository not provided in serializer context.")

        messages_data = validated_data.pop("messages", [])
        chat_room = ChatRoom(**validated_data)
        mongo_container.create_chatroom(chat_room)

        for msg_data in messages_data:
            message = Message(**msg_data)
            mongo_container.add_message(chat_room.room_id, message)

        return chat_room
