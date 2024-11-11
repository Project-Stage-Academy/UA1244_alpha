import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Mapping, Any, List, Dict

from cryptography.fernet import Fernet
from django.conf import settings
from pymongo import MongoClient
from pymongo.synchronous.collection import Collection

from communications.domain.entities.messages import ChatRoom, Message
from communications.domain.values.messages import Text
from communications.repositories.filters import GetMessagesFilters

logger = logging.getLogger('django')

cipher_suite = Fernet(settings.ENCRYPTION_KEY)


@dataclass
class BaseRepository(ABC):
    mongo_db_client: MongoClient
    mongo_db_db_name: str
    mongo_db_collection_name: str

    @property
    def _collection(self) -> Collection[Mapping[str, Any]]:
        return self.mongo_db_client[self.mongo_db_db_name][self.mongo_db_collection_name]

    def _decrypt_message(self, encrypted_message: dict) -> Optional[Message]:
        """Decrypt the message content and return a Message object."""
        try:
            decrypted_content = cipher_suite.decrypt(encrypted_message['content']).decode()
            message_data = {k: v for k, v in encrypted_message.items() if k != 'content'}
            message_data['content'] = decrypted_content
            decrypted_message = Message(**message_data)
            return decrypted_message
        except Exception as e:
            logger.error(f"Failed to decrypt message: {e}", exc_info=True)
            return None


class BaseChatsRepository(BaseRepository):
    @abstractmethod
    def create_chatroom(self, chatroom: ChatRoom) -> None:
        """Create a new chatroom in the repository."""
        pass

    @abstractmethod
    def get_chatroom(self, room_oid: str) -> Optional[ChatRoom]:
        """Retrieve a chatroom by its room_oid. Return None if not found."""
        pass

    @abstractmethod
    def get_user_chats(self, user_id: str) -> List[Dict]:
        ...


class BaseMessagesRepository(BaseRepository):
    @abstractmethod
    def create_message(self, room_oid: str, message: Message) -> None:
        """Add a message to a chatroom."""
        pass

    @abstractmethod
    def get_messages(self, room_oid: str, filters: GetMessagesFilters) -> List[Message]:
        """Retrieve messages from a chatroom based on given filters."""
        pass

    @abstractmethod
    def get_message_by_id(self, message_oid: str) -> Optional[Message]:
        pass
