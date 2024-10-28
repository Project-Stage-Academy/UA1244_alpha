from abc import ABC, abstractmethod
from dataclasses import dataclass

from communications.entities.messages import Message


@dataclass
class BaseEvent(ABC):

    @abstractmethod
    def trigger(self, message: Message):
        """Abstract method to be implemented for triggering the notification event."""
        ...
