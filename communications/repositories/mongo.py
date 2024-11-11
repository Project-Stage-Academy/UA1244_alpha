import logging
from dataclasses import dataclass
from typing import Optional, List, Dict

from cryptography.fernet import Fernet
from django.conf import settings
from pymongo.errors import PyMongoError

from communications.domain.entities.messages import ChatRoom, Message
from .base import BaseMessagesRepository, BaseChatsRepository
from .filters import GetMessagesFilters

logger = logging.getLogger('django')

cipher_suite = Fernet(settings.ENCRYPTION_KEY)


@dataclass
class MongoDBChatsRepositories(BaseChatsRepository):

    def create_chatroom(self, chatroom: ChatRoom):
        try:
            self._collection.insert_one(chatroom.__dict__)
            logger.info(f"Chatroom created successfully with ID: {chatroom.oid}")
        except PyMongoError as e:
            logger.error(f"Error creating chatroom: {e}", exc_info=True)

    def get_chatroom(self, room_oid: str) -> Optional[ChatRoom]:
        try:
            data = self._collection.find_one({"oid": room_oid})

            if data:
                messages = [self._decrypt_message(msg) for msg in data.get('messages', [])]
                chatroom = ChatRoom(
                    title=data['title'],
                    sender_id=data.get('sender_id'),
                    receiver_id=data.get('receiver_id'),
                    messages=messages
                )
                logger.info(f"Chatroom retrieved successfully: {chatroom}")
                return chatroom

            logger.warning(f"Chatroom with ID: {room_oid} not found.")
            return None
        except PyMongoError as e:
            logger.error(f"Error retrieving chatroom: {e}", exc_info=True)
            return None

    def get_user_chats(self, user_id: str) -> List[Dict]:
        try:
            chat_rooms = self._collection.find({
                "$or": [{"sender_id": user_id}, {"receiver_id": user_id}]
            }, {"messages": 0})

            formatted_chat_rooms = []
            for chat in chat_rooms:
                if '_id' in chat:
                    del chat['_id']

                formatted_chat_rooms.append(ChatRoom(**chat).__dict__)

            return formatted_chat_rooms
        except PyMongoError as e:
            logger.error(f"Error retrieving chat rooms for user_id {user_id}: {e}", exc_info=True)
            return []


@dataclass
class MongoDBMessagesRepositories(BaseMessagesRepository):
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

    def get_message_by_id(self, message_id: str) -> Optional[Message]:
        """
        Retrieve a specific message by its `message_id` across all chatrooms.
        """
        try:
            result = self._collection.aggregate([
                {"$unwind": "$messages"},
                {"$match": {"messages.oid": message_id}},
                {"$project": {"_id": 0, "messages": 1}}
            ])

            message_data = next(result, {}).get("messages")

            if message_data:
                message_data['content'] = cipher_suite.decrypt(message_data['content']).decode()
                message = Message(**message_data)
                logger.info(f"Message with ID {message_id} retrieved successfully.")
                return message

            logger.warning(f"Message with ID {message_id} not found.")
            return None

        except PyMongoError as e:
            logger.error(f"Error retrieving message with ID {message_id}: {e}", exc_info=True)
            return None
