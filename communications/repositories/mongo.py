import logging
from dataclasses import dataclass
from typing import Any, Mapping, Optional

from cryptography.fernet import Fernet
from django.conf import settings
from pymongo import MongoClient
from pymongo.synchronous.collection import Collection
from pymongo.errors import PyMongoError

from communications.domain.entities.messages import ChatRoom, Message
from .base import BaseRepository
from .filters import GetMessagesFilters

logger = logging.getLogger('django')

cipher_suite = Fernet(settings.ENCRYPTION_KEY)


@dataclass
class MongoDBRepository(BaseRepository):
    mongo_db_client: MongoClient
    mongo_db_db_name: str
    mongo_db_collection_name: str

    @property
    def _collection(self) -> Collection[Mapping[str, Any]]:
        return self.mongo_db_client[self.mongo_db_db_name][self.mongo_db_collection_name]

    def create_chatroom(self, chatroom: ChatRoom):
        try:
            self._collection.insert_one(chatroom.__dict__)
            logger.info(f"Chatroom created successfully with ID: {chatroom.oid}")
        except PyMongoError as e:
            logger.error(f"Error creating chatroom: {e}", exc_info=True)

    def create_message(self, room_oid: str, message: Message):
        message_dict = message.__dict__
        logger.info(f"Adding message to chatroom ID: {room_oid} - Message: {message.oid}")
        message_dict['content'] = cipher_suite.encrypt(
            message.content.as_generic_type().encode()
        )

        try:
            result = self._collection.update_one(
                {"oid": room_oid},
                {"$push": {"messages": message_dict}}
            )

            if result.modified_count > 0:
                logger.info("Message added successfully.")
            else:
                logger.warning(f"Failed to add message to chatroom ID: {room_oid}. Room may not exist.")
        except PyMongoError as e:
            logger.error(f"Error adding message to chatroom ID {room_oid}: {e}", exc_info=True)

    def get_chatroom(self, room_oid: str) -> Optional[ChatRoom]:
        try:
            data = self._collection.find_one({"oid": room_oid})

            if data:
                messages = [self._decrypt_message(msg) for msg in data.get('messages', [])]
                chatroom = ChatRoom(
                    title=data['title'],
                    startup_id=data.get('startup_id'),
                    investor_id=data.get('investor_id'),
                    messages=messages
                )
                logger.info(f"Chatroom retrieved successfully: {chatroom}")
                return chatroom

            logger.warning(f"Chatroom with ID: {room_oid} not found.")
            return None
        except PyMongoError as e:
            logger.error(f"Error retrieving chatroom: {e}", exc_info=True)
            return None

    def get_messages(self, room_oid: str, filters: GetMessagesFilters) -> list[Message]:
        """Retrieve messages for a specific chat room with pagination using filters."""
        try:
            cursor = self._collection.find({"room_oid": room_oid})

            cursor = cursor.skip(filters.offset).limit(filters.limit)

            messages = [Message(**message) for message in cursor]
            return messages
        except PyMongoError as e:
            logger.error(f"Failed to retrieve messages for chat room with ID {room_oid}: {e}", exc_info=True)
            return []

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