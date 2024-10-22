from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import List, Optional

from communications.entities.base import BaseEntity


@dataclass
class Message(BaseEntity):
    sender_id: int
    receiver_id: int
    content: str
    read_at: Optional[datetime] = None

    def mark_as_read(self):
        """Mark the message as read by setting the read_at timestamp."""
        self.read_at = datetime.now()


@dataclass
class ChatRoom(BaseEntity):
    room_id: str
    startup_id: int
    investor_id: int
    messages: List[Message] = field(default_factory=list)

    def add_message(self, message: Message):
        """Add a new message to the room."""
        self.messages.append(message)

    def get_unread_messages(self) -> List[Message]:
        """Return a list of unread messages in the room."""
        return [message for message in self.messages if message.read_at is None]
