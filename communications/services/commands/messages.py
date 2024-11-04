from dataclasses import dataclass

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

    async def handle(self, room_oid: str, message: Message):
        chat = await self.chat_query.handle(room_oid)

        await self.messege_event.trigger(message=message, chat=chat)
        self.mongo_repo.create_message(room_oid, message)

