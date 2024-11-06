import logging
from dataclasses import dataclass
from typing import Optional

from communications.domain.entities.messages import ChatRoom, Message
from communications.repositories.base import BaseChatsRepository, BaseMessagesRepository
from communications.repositories.filters import GetMessagesFilters
from communications.services.queries.base import BaseQuery

logger = logging.getLogger('django')


@dataclass
class ChatRoomQuery(BaseQuery):
    mongo_repo: BaseChatsRepository

    def handle(self, room_oid: str) -> Optional[ChatRoom]:
        """Retrieve a chat room by its unique identifier."""
        chat = self.mongo_repo.get_chatroom(room_oid)
        return chat


@dataclass
class MessageQuery(BaseQuery):
    mongo_repo: BaseMessagesRepository

    def handle(self, room_oid: str, filters: GetMessagesFilters) -> list[Message]:
        """Retrieve all messages for a specific chat room."""
        messages = self.mongo_repo.get_messages(room_oid, filters)
        return messages
