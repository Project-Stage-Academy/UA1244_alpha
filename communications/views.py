from dataclasses import asdict
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import MessageSerializer, ChatRoomSerializer
from communications import init_container, MongoDBRepository

container = init_container()
mongo_container = container.resolve(MongoDBRepository)


class CreateChatRoomView(APIView):
    """
    View for creating a new chat room between a startup and an investor.
    """

    def post(self, request):
        serializer = ChatRoomSerializer(data=request.data)
        if serializer.is_valid():
            chat_room = serializer.create(serializer.validated_data)
            return Response({'room_id': str(chat_room.room_id)}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SendMessageView(APIView):
    """
    View for sending a message in a specific chat room.
    """

    def post(self, request, room_id):
        """
        Sends a message in the specified chat room.
        """
        request_data = request.data.copy()
        request_data['room_id'] = room_id
        if 'sender_id' not in request_data:
            return Response({'error': 'sender_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = MessageSerializer(data=request_data)
        if serializer.is_valid():
            message = serializer.create(serializer.validated_data)
            mongo_container.add_message(room_id, message)
            return Response({'message_id': str(message.oid)}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ListMessagesView(APIView):
    """
    View for listing all messages in a specific chat room.
    """

    def get(self, request, room_id):
        """
        Retrieve all messages in a specific chat room, sorted by creation date.

        """
        chat_room = mongo_container.get_chatroom(room_id)

        if chat_room:
            message_list = sorted(
                (asdict(msg) for msg in chat_room.messages),
                key=lambda msg: msg.get('created_at'),
                reverse=False
            )
            return Response(message_list, status=status.HTTP_200_OK)

        return Response({'error': 'Chat room not found.'}, status=status.HTTP_404_NOT_FOUND)

