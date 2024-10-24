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

    def create(self, validated_data):
        """Create a new Message instance from validated data and save it in MongoDB."""
        message = Message(**validated_data)
        mongo_container.add_message(validated_data['room_id'], message)
        return message


class ChatRoomSerializer(serializers.Serializer):
    """Serializer for representing a chat root between
    a startup and an investor"""

    room_id = serializers.CharField()
    startup_id = serializers.IntegerField()
    investor_id = serializers.IntegerField()

    def create(self, validated_data):
        """Create a new ChatRoom instance and save it to MongoDB"""

        messages_data = validated_data.pop("messages", [])
        chat_room = ChatRoom(**validated_data)
        mongo_container.create_chatroom(chat_room)

        for msg_data in messages_data:
            message = Message(**msg_data)
            mongo_container.add_message(chat_room.room_id, message)

        return chat_room
