# views.py

import logging
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .permissions import IsOwnerOrRecipient
from .logic import ChatRoomService, MessageService, ListMessagesService

logger = logging.getLogger(__name__)


class CreateChatRoomView(APIView):
    """
    View for creating a new chat room between a startup and an investor.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            chat_room = ChatRoomService.create_chat_room(request.data)
            return Response({'room_oid': str(chat_room.oid)}, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response(e.args[0], status=status.HTTP_400_BAD_REQUEST)
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
    permission_classes = (IsOwnerOrRecipient, IsAuthenticated)

    def post(self, request, room_oid):
        try:
            message = MessageService.send_message(request.data, room_oid)
            return Response(data={'message_id': str(message.oid)}, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response(data=e.args[0], status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
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
            message_list = ListMessagesService.list_messages(room_oid)
            return Response(message_list, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response(data=e.args[0], status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Failed to list messages for room {room_oid}: {e}", exc_info=True)
            return Response(
                data={'error': 'Failed to retrieve messages due to server error.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
