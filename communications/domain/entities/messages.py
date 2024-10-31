import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from communications.domain.entities.base import BaseEntity
from communications.domain.values.messages import Title, Text

logger = logging.getLogger('django')


@dataclass
class Message(BaseEntity):
    sender_id: int
    receiver_id: int
    content: Text
    read_at: Optional[datetime] = None

    def mark_as_read(self):
        """Mark the message as read by setting the read_at timestamp."""
        self.read_at = datetime.now()
        logger.info(f"Message {self.oid} marked as read at {self.read_at}")


@dataclass
class ChatRoom(BaseEntity):
    title: Title
    startup_id: int
    investor_id: int
    messages: List[Message] = field(default_factory=list)

    @classmethod
    def create_chat(cls, title: Title, startup_id: int, investor_id: int, messages: Optional[List[Message]] = None):
        """Factory method to create a new chat room instance."""
        return cls(
            title=title,
            startup_id=startup_id,
            investor_id=investor_id,
            messages=messages or []
        )

    def add_message(self, message: Message):
        """Add a new message to the room."""
        self.messages.append(message)
        logger.info(f"Message {message.oid} added to ChatRoom {self.title}")
