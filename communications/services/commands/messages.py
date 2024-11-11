from dataclasses import dataclass

from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist

from communications.domain.values.messages import Text
from communications.events.base import BaseEvent
from communications.domain.entities.messages import ChatRoom, Message
from communications.repositories.base import BaseChatsRepository, BaseMessagesRepository
from communications.services.commands.base import BaseCommand
from communications.services.queries.messages import ChatRoomQuery


@dataclass(frozen=True)
class CreateChatCommand(BaseCommand):
    mongo_repo: BaseChatsRepository

    async def handle(self, chat_room: ChatRoom):
        self.mongo_repo.create_chatroom(chat_room)


@dataclass(frozen=True)
class CreateMessageCommand(BaseCommand):
    mongo_repo: BaseMessagesRepository
    messege_event: BaseEvent
    chat_query: ChatRoomQuery

    async def handle(self, user_id: int, room_oid: str, message_data: str) -> dict:
        chat = self.chat_query.handle(room_oid)

        if user_id != chat.sender_id:
            chat.sender_id, chat.receiver_id = user_id, chat.sender_id

        user = get_user_model()

        try:
            sender_user = await sync_to_async(user.objects.get)(id=chat.sender_id)
        except ObjectDoesNotExist as e:
            raise ValueError(f"User not found: {e}")

        message = Message(
            content=Text(message_data),
            sender_id=chat.sender_id,
            receiver_id=chat.receiver_id,
        )
        self.mongo_repo.create_message(room_oid, message)
        await self.messege_event.trigger(message=message, chat=chat)

        return {
            "oid": message.oid,
            "content": message.content,
            "sender_id": message.sender_id,
            "receiver_id": message.receiver_id,
            "created_at": message.created_at,
            "sender_name": sender_user.first_name,
        }
