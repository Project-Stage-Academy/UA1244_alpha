import logging
from dataclasses import asdict
from django_ratelimit.decorators import ratelimit
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .permissions import IsOwnerOrRecipient
from .serializers import MessageSerializer, ChatRoomSerializer
from communications import init_container, MongoDBRepository


logger = logging.getLogger(__name__)

container = init_container()
mongo_container = container.resolve(MongoDBRepository)


class CreateChatRoomView(APIView):
    """
    View for creating a new chat room between a startup and an investor.
    """

    @ratelimit(key='ip', rate='10/m', method='POST', block=True)
    def post(self, request):
        serializer = ChatRoomSerializer(data=request.data)

        if serializer.is_valid():
            chat_room = serializer.create(serializer.validated_data)
            logger.info(f"Chat room created with ID: {chat_room.room_id}")

            return Response({'room_id': str(chat_room.room_id)}, status=status.HTTP_201_CREATED)

        logger.warning(f"Invalid data for creating chat room: {serializer.errors}")

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SendMessageView(APIView):
    """
    View for sending a message in a specific chat room.
    """
    permission_classes = (IsOwnerOrRecipient,)

    @ratelimit(key='ip', rate='20/m', method='POST', block=True)
    def post(self, request, room_id):
        logger.info(f"SendMessageView POST request received for room_id: {room_id}")

        request_data = request.data.copy()
        request_data['room_id'] = room_id
        if 'sender_id' not in request_data:
            logger.error("sender_id is required in the request data")
            return Response({'error': 'sender_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = MessageSerializer(data=request_data)
        if serializer.is_valid():
            message = serializer.create(serializer.validated_data)
            mongo_container.add_message(room_id, message)
            logger.info(f"Message sent with ID: {message.oid} in room: {room_id}")
            return Response({'message_id': str(message.oid)}, status=status.HTTP_201_CREATED)

        logger.warning(f"Invalid data for sending message: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ListMessagesView(APIView):
    """
    View for listing all messages in a specific chat room.
    """
    permission_classes = (IsOwnerOrRecipient,)

    @ratelimit(key='ip', rate='10/m', method='GET', block=True)
    def get(self, request, room_id):
        logger.info(f"ListMessagesView GET request received for room_id: {room_id}")

        chat_room = mongo_container.get_chatroom(room_id)
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
