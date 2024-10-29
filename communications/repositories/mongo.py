import logging
from dataclasses import dataclass
from typing import Any, Mapping

from cryptography.fernet import Fernet
from django.conf import settings
from pymongo import MongoClient
from pymongo.synchronous.collection import Collection

from communications.domain.entities.messages import ChatRoom, Message
from .base import BaseRepository

logger = logging.getLogger(__name__)

cipher_suite = Fernet(settings.ENCRYPTION_KEY)


@dataclass
class MongoDBRepository(BaseRepository):
    mongo_db_client: MongoClient
    mongo_db_db_name: str
    mongo_db_collection_name: str

    @property
    def _collection(self) -> Collection[Mapping[str, Any] | Any]:
        return self.mongo_db_client[self.mongo_db_db_name][self.mongo_db_collection_name]

    def _decrypt_message(self, encrypted_message: dict) -> Message:
        """Decrypt the message content and return a Message object."""
        decrypted_content = cipher_suite.decrypt(encrypted_message['content']).decode()
        message_data = {k: v for k, v in encrypted_message.items() if k != 'content'}
        message_data['content'] = decrypted_content
        decrypted_message = Message(**message_data)
        return decrypted_message

    def create_chatroom(self, chatroom: ChatRoom):
        self._collection.insert_one(chatroom.__dict__)
        logger.info(f"Chatroom created successfully with ID: {chatroom.title}")

    def get_chatroom(self, room_id: str) -> ChatRoom | None:
        logger.info(f"Retrieving chatroom with ID: {room_id}")
        data = self._collection.find_one({"room_id": room_id})

        if data:
            messages = [self._decrypt_message(msg) for msg in data.get('messages', [])]
            chatroom = ChatRoom(
                title=data['room_id'],
                startup_id=data.get('startup_id'),
                investor_id=data.get('investor_id'),
                messages=messages
            )
            logger.info(f"Chatroom retrieved successfully: {chatroom}")
            return chatroom

        logger.warning(f"Chatroom with ID: {room_id} not found.")
        return None

    def add_message(self, room_id: str, message: Message):
        message_dict = message.__dict__
        logger.info(f"Adding message to chatroom ID: {room_id} - Message: {message.oid}")

        message_dict['content'] = cipher_suite.encrypt(
            message.content.as_generic_type().encode()
        )

        result = self._collection.update_one(
            {"room_id": room_id},
            {"$push": {"messages": message_dict}}
        )

        if result.modified_count > 0:
            logger.info("Message added successfully.")
        else:
            logger.warning(f"Failed to add message to chatroom ID: {room_id}. Room may not exist.")
