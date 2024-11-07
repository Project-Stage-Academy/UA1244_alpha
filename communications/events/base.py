from abc import ABC, abstractmethod
from dataclasses import dataclass

from communications.domain.entities.messages import Message, ChatRoom


@dataclass
class BaseEvent(ABC):

    @abstractmethod
    def trigger(self, message: Message, chat: ChatRoom):
        """Abstract method to be implemented for triggering the notification event."""
        ...
