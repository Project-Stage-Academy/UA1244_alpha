import logging
from dataclasses import dataclass
from typing import Any, Mapping, Optional

from cryptography.fernet import Fernet
from django.conf import settings
from pymongo import MongoClient
from pymongo.synchronous.collection import Collection
from pymongo.errors import PyMongoError

from communications.entities.messages import ChatRoom, Message
from .base import BaseRepository

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

    def _decrypt_message(self, encrypted_message: dict) -> Optional[Message]:
        """Decrypt the message content and return a Message object."""
        try:
            decrypted_content = cipher_suite.decrypt(encrypted_message['content']).decode()
            decrypted_message = Message(**encrypted_message, content=decrypted_content)
            return decrypted_message
        except Exception as e:
            logger.error(f"Failed to decrypt message: {e}", exc_info=True)
            return None

    def create_chatroom(self, chatroom: ChatRoom):
        chatroom_dict = chatroom.__dict__
        chatroom_dict['messages'] = [
            {**message.__dict__, 'content': cipher_suite.encrypt(message.content.encode())}
            for message in chatroom.messages
        ]

        logger.info(f"Creating chatroom with ID: {chatroom.room_id}")

        try:
            self._collection.insert_one(chatroom_dict)
            logger.info(f"Chatroom created successfully: {chatroom_dict}")
        except PyMongoError as e:
            logger.error(f"Error creating chatroom: {e}", exc_info=True)

    def get_chatroom(self, room_id: str) -> Optional[ChatRoom]:
        logger.info(f"Retrieving chatroom with ID: {room_id}")
        try:
            data = self._collection.find_one({"room_id": room_id})

            if data:
                messages = [self._decrypt_message(msg) for msg in data.get('messages', [])]
                chatroom = ChatRoom(
                    room_id=data['room_id'],
                    startup_id=data.get('startup_id'),
                    investor_id=data.get('investor_id'),
                    messages=messages
                )
                logger.info(f"Chatroom retrieved successfully: {chatroom}")
                return chatroom

            logger.warning(f"Chatroom with ID: {room_id} not found.")
            return None
        except PyMongoError as e:
            logger.error(f"Error retrieving chatroom: {e}", exc_info=True)
            return None

    def add_message(self, room_id: str, message: Message):
        message_dict = message.__dict__
        logger.info(f"Adding message to chatroom ID: {room_id} - Message: {message_dict}")

        message_dict['content'] = cipher_suite.encrypt(message.content.encode())

        try:
            result = self._collection.update_one(
                {"room_id": room_id},
                {"$push": {"messages": message_dict}}
            )

            if result.modified_count > 0:
                logger.info("Message added successfully.")
            else:
                logger.warning(f"Failed to add message to chatroom ID: {room_id}. Room may not exist.")
        except PyMongoError as e:
            logger.error(f"Error adding message to chatroom ID {room_id}: {e}", exc_info=True)
