import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from communications.domain.entities.base import BaseEntity
from communications.domain.values.messages import Title, Text

logger = logging.getLogger('django')


@dataclass
class Message(BaseEntity):
    content: Text
    sender_id: int
    receiver_id: int
    read_at: Optional[datetime] = None

    def mark_as_read(self):
        """Mark the message as read by setting the read_at timestamp."""
        self.read_at = datetime.now()
        logger.info(f"Message {self.oid} marked as read at {self.read_at}")


@dataclass
class ChatRoom(BaseEntity):
    title: Title
    sender_id: int
    receiver_id: int
    messages: List[Message] = field(default_factory=list)
