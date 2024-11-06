import logging
from dataclasses import asdict

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from communications import init_container, MongoDBRepository
from .permissions import IsOwnerOrRecipient
from .serializers import MessageSerializer, ChatRoomSerializer

logger = logging.getLogger(__name__)

container = init_container()
mongo_repo = container.resolve(MongoDBRepository)


class CreateChatRoomView(APIView):
    """
    View for creating a new chat room between a startup and an investor.
    """

    def post(self, request):
        try:
            serializer = ChatRoomSerializer(data=request.data, context={'mongo_repo': mongo_repo})

            if serializer.is_valid():
                chat_room = serializer.create(serializer.validated_data)
                logger.info(f"Chat room created with ID: {chat_room.room_id}")
                return Response({'room_id': str(chat_room.room_id)}, status=status.HTTP_201_CREATED)

            logger.warning(f"Invalid data for creating chat room: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Failed to create chat room: {e}", exc_info=True)
            return Response(
                {'error': 'Failed to create chat room due to server error.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SendMessageView(APIView):
    """
    View for sending a message in a specific chat room.
    """
    permission_classes = (IsOwnerOrRecipient,)

    def post(self, request, room_id):
        try:
            logger.info(f"SendMessageView POST request received for room_id: {room_id}")

            chat_room = mongo_repo.get_chatroom(room_id)
            if chat_room is None:
                logger.error(f"Chat room with ID {room_id} does not exist.")
                return Response({'error': 'Chat room not found.'}, status=status.HTTP_404_NOT_FOUND)

            if 'sender_id' not in request.data:
                logger.error("sender_id is required in the request data")
                return Response({'error': 'sender_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

            serializer = MessageSerializer(data=request.data, context={'mongo_repo': mongo_repo, 'room_id': room_id})
            if serializer.is_valid():
                message = serializer.save()
                logger.info(f"Message sent with ID: {message.oid} in room: {room_id}")
                return Response({'message_id': str(message.oid)}, status=status.HTTP_201_CREATED)

            logger.warning(f"Invalid data for sending message: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Failed to send message in room {room_id}: {e}", exc_info=True)
            return Response(
                {'error': 'Failed to send message due to server error.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ListMessagesView(APIView):
    """
    View for listing all messages in a specific chat room.
    """
    permission_classes = (IsOwnerOrRecipient,)

    def get(self, request, room_id):
        try:
            logger.info(f"ListMessagesView GET request received for room_id: {room_id}")

            chat_room = mongo_repo.get_chatroom(room_id)
            if chat_room:
                message_list = sorted(
                    (asdict(msg) for msg in chat_room.messages),
                    key=lambda msg: msg.get('created_at'),
                    reverse=False
                )
                logger.info(f"Retrieved {len(message_list)} messages for room_id: {room_id}")
                return Response(message_list, status=status.HTTP_200_OK)

            logger.error(f"Chat room not found for room_id: {room_id}")
            return Response({'error': 'Chat room not found.'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            logger.error(f"Failed to list messages for room {room_id}: {e}", exc_info=True)
            return Response(
                {'error': 'Failed to retrieve messages due to server error.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
