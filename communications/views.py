import logging
from dataclasses import asdict

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from communications.repositories.base import BaseChatsRepository, BaseMessagesRepository
from communications.di_container import init_container
from investors.models import InvestorProfile
from startups.models import StartUpProfile
from .consumers.messages import get_chat_room_query, create_message_command
from .domain.entities.messages import ChatRoom, Message
from .domain.exceptions.base import ApplicationException
from .permissions import IsOwnerOrRecipient
from .serializers import MessageSerializer, ChatRoomSerializer
from .services.commands.messages import CreateMessageCommand
from .services.queries.messages import ChatRoomQuery

logger = logging.getLogger(__name__)

container = init_container()
mongo_chats_repo: BaseChatsRepository = container.resolve(BaseChatsRepository)
mongo_messages_repo: BaseMessagesRepository = container.resolve(BaseMessagesRepository)
get_chat_room_query: ChatRoomQuery = container.resolve(ChatRoomQuery)
create_message_command: CreateMessageCommand = container.resolve(CreateMessageCommand)


class CreateChatRoomView(APIView):
    """
    View for creating a new chat room between a startup and an investor.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChatRoomSerializer(data=request.data, context={'mongo_chats_repo': mongo_chats_repo})

        if not serializer.is_valid():
            logger.warning(f"Invalid data for creating chat room: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        sender_id = serializer.validated_data['sender_id']
        receiver_id = serializer.validated_data['receiver_id']

        if not StartUpProfile.objects.filter(id=sender_id).exists():
            return Response({'error': 'Startup not found.'}, status=status.HTTP_404_NOT_FOUND)

        if not InvestorProfile.objects.filter(id=receiver_id).exists():
            return Response({'error': 'Investor not found.'}, status=status.HTTP_404_NOT_FOUND)

        try:
            chat_room: ChatRoom = serializer.save()
            logger.info(f"Chat room created with ID: {chat_room.oid}")
            return Response({'room_oid': str(chat_room.oid)}, status=status.HTTP_201_CREATED)
        except ApplicationException as e:
            logger.error(f"Failed to create chat room: {e}", exc_info=True)
            return Response(
                {'error': 'Failed to create chat room due to server error.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SendMessageView(APIView):
    """
    View for sending a message in a specific chat room.
    """
    permission_classes = (IsOwnerOrRecipient, IsAuthenticated)

    def post(self, request, room_oid):
        logger.info(f"SendMessageView POST request received for room_oid: {room_oid}")

        try:
            serializer = MessageSerializer(data=request.data)
            if serializer.is_valid():
                message: Message = create_message_command.handle(
                    user_id=request.user.id,
                    room_oid=room_oid,
                    message_data=request.data.get('content')
                )
                logger.info(f"Message sent with ID: {message.oid} in room: {room_oid}")
                return Response(data={'message_id': str(message.oid)}, status=status.HTTP_201_CREATED)

            logger.warning(f"Invalid data for sending message: {serializer.errors}")
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except ApplicationException as e:
            logger.error(f"Failed to send message in room {room_oid}: {e}", exc_info=True)
            return Response(
                data={'error': 'Failed to send message due to server error.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ListMessagesView(APIView):
    """
    View for listing all messages in a specific chat room.
    """
    permission_classes = (IsOwnerOrRecipient,)

    def get(self, request, room_oid):
        try:
            logger.info(f"ListMessagesView GET request received for room_oid: {room_oid}")

            chat_room: ChatRoom = mongo_chats_repo.get_chatroom(room_oid)
            if chat_room:
                message_list = sorted(
                    (asdict(msg) for msg in chat_room.messages),
                    key=lambda msg: msg.get('created_at'),
                    reverse=False
                )
                logger.info(f"Retrieved {len(message_list)} messages for room_oid: {room_oid}")
                return Response(message_list, status=status.HTTP_200_OK)

            logger.error(f"Chat room not found for room_oid: {room_oid}")
            return Response(data={'error': 'Chat room not found.'}, status=status.HTTP_404_NOT_FOUND)

        except ApplicationException as e:
            logger.error(f"Failed to list messages for room {room_oid}: {e}", exc_info=True)
            return Response(
                data={'error': 'Failed to retrieve messages due to server error.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
