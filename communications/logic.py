import logging
from dataclasses import asdict

from investors.models import InvestorProfile
from startups.models import StartUpProfile
from .serializers import MessageSerializer, ChatRoomSerializer
from communications.repositories.base import BaseChatsRepository, BaseMessagesRepository
from communications.di_container import init_container

logger = logging.getLogger(__name__)

container = init_container()
mongo_chats_repo: BaseChatsRepository = container.resolve(BaseChatsRepository)
mongo_messages_repo: BaseMessagesRepository = container.resolve(BaseMessagesRepository)


class ChatRoomService:
    """Service for handling chat room operations."""

    @staticmethod
    def create_chat_room(data):
        serializer = ChatRoomSerializer(data=data, context={'mongo_chats_repo': mongo_chats_repo})

        if not serializer.is_valid():
            logger.warning(f"Invalid data for creating chat room: {serializer.errors}")
            raise ValueError(serializer.errors)

        sender_id = serializer.validated_data['sender_id']
        receiver_id = serializer.validated_data['receiver_id']

        if not StartUpProfile.objects.filter(id=sender_id).exists():
            raise ValueError({'error': 'Startup not found.'})

        if not InvestorProfile.objects.filter(id=receiver_id).exists():
            raise ValueError({'error': 'Investor not found.'})

        chat_room = serializer.save()
        logger.info(f"Chat room created with ID: {chat_room.oid}")
        return chat_room


class MessageService:
    """Service for handling message operations."""

    @staticmethod
    def send_message(data, room_oid):
        serializer = MessageSerializer(
            data=data,
            context={'mongo_messages_repo': mongo_messages_repo, 'room_oid': room_oid}
        )

        if not serializer.is_valid():
            logger.warning(f"Invalid data for sending message: {serializer.errors}")
            raise ValueError(serializer.errors)

        message = serializer.save()
        logger.info(f"Message sent with ID: {message.oid} in room: {room_oid}")
        return message


class ListMessagesService:
    """Service for retrieving messages in a chat room."""

    @staticmethod
    def list_messages(room_oid):
        chat_room = mongo_chats_repo.get_chatroom(room_oid)
        if not chat_room:
            raise ValueError({'error': 'Chat room not found.'})

        message_list = sorted(
            (asdict(msg) for msg in chat_room.messages),
            key=lambda msg: msg.get('created_at')
        )
        logger.info(f"Retrieved {len(message_list)} messages for room_oid: {room_oid}")
        return message_list
