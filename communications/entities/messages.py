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


@dataclass
class ChatRoom(BaseEntity):
    room_id: str
    startup_id: int
    investor_id: int
    messages: List[Message] = field(default_factory=list)
