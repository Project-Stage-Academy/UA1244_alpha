from dataclasses import dataclass

from asgiref.sync import sync_to_async

from communications import BaseEvent
from communications.domain.entities.messages import ChatRoom, Message
from communications.repositories.base import BaseRepository


@dataclass(frozen=True)
class CreateChatCommand:
    mongo_repo: BaseRepository

    async def handle(self, chat_room: ChatRoom):
        self.mongo_repo.create_chatroom(chat_room)


@dataclass(frozen=True)
class CreateMessageCommand:
    mongo_repo: BaseRepository
    messege_event: BaseEvent

    async def handle(self, room_oid: str, message: Message):
        self.mongo_repo.add_message(room_oid, message)
        self.messege_event.trigger(message=message)
