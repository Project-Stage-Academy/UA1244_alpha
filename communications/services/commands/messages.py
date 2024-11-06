from dataclasses import dataclass

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

    def handle(self, user_id: int, room_oid: str, message_data: dict) -> Message:
        chat = self.chat_query.handle(room_oid)

        if user_id != chat.sender_id:
            chat.sender_id, chat.receiver_id = user_id, chat.sender_id

        message = Message(
            content=Text(message_data['content']),
            sender_id=chat.sender_id,
            receiver_id=chat.receiver_id,
            read_at=message_data.get('read_at')
        )

        self.mongo_repo.create_message(room_oid, message)
        self.messege_event.trigger(message=message, chat=chat)

        return message

