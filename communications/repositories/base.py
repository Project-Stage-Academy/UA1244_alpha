from abc import ABC, abstractmethod
from typing import Optional

from communications.domain.entities.messages import (
    ChatRoom,
    Message
)


class BaseRepository(ABC):
    @abstractmethod
    def create_chatroom(self, chatroom: ChatRoom) -> None:
        """Create a new chatroom in the repository."""
        pass

    @abstractmethod
    def get_chatroom(self, room_id: str) -> Optional[ChatRoom]:
        """Retrieve a chatroom by its room_id. Return None if not found."""
        pass

    @abstractmethod
    def add_message(self, room_id: str, message: Message) -> None:
        """Add a message to a chatroom."""
        pass
