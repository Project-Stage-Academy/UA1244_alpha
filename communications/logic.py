import logging
from dataclasses import asdict

from django.contrib.auth import get_user_model

from communications.di_container import init_container
from communications.repositories.base import BaseChatsRepository, BaseMessagesRepository
from investors.models import InvestorProfile
from startups.models import StartUpProfile
from .serializers import MessageSerializer, ChatRoomSerializer

logger = logging.getLogger(__name__)

container = init_container()
mongo_chats_repo: BaseChatsRepository = container.resolve(BaseChatsRepository)
mongo_messages_repo: BaseMessagesRepository = container.resolve(BaseMessagesRepository)

User = get_user_model()


class ChatRoomService:
    """Service for handling chat room operations."""

    @staticmethod
    def create_chat_room(data, user):
        serializer = ChatRoomSerializer(data=data, context={'mongo_chats_repo': mongo_chats_repo, 'user': user})

        if not serializer.is_valid():
            logger.warning(f"Invalid data for creating chat room: {serializer.errors}")
            raise ValueError(serializer.errors)

        receiver_id = serializer.validated_data['receiver_id']

        user_exists = User.objects.filter(id__in=[receiver_id, user]).count()
        if user_exists < 2:
            missing_user = 'Sender' if user not in [receiver_id] else 'Receiver'
            raise ValueError({'error': f"{missing_user} not found."})

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


class ListUserChatsService:
    """Service for retrieving all chat rooms associated with a user."""

    @staticmethod
    def list_user_chats(user_id):
        chat_rooms = mongo_chats_repo.get_user_chats(user_id)
        if not chat_rooms:
            raise ValueError({'error': 'No chat rooms found for this user.'})

        logger.info(f"Retrieved {len(chat_rooms)} chat rooms for user_id: {user_id}")
        return chat_rooms
