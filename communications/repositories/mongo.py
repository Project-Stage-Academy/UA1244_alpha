from dataclasses import dataclass
from bson import ObjectId
from pymongo import MongoClient
import logging
from .base import BaseRepository
from communications.entities.messages import ChatRoom, Message


logger = logging.getLogger('django')

@dataclass
class MongoDBRepository(BaseRepository):
    mongo_db_client: MongoClient
    mongo_db_db_name: str
    mongo_db_collection_name: str

    @property
    def _collection(self):
        return self.mongo_db_client[self.mongo_db_db_name][self.mongo_db_collection_name]

    def create_chatroom(self, chatroom: ChatRoom):
        chatroom_dict = chatroom.__dict__
        chatroom_dict['messages'] = [message.__dict__ for message in chatroom.messages]

        logger.info(f"Creating chatroom with ID: {chatroom.room_id}")

        self._collection.insert_one(chatroom_dict)

        logger.info(f"Chatroom created successfully: {chatroom_dict}")

    def get_chatroom(self, room_id: str) -> ChatRoom:
        logger.info(f"Retrieving chatroom with ID: {room_id}")
        data = self._collection.find_one({"room_id": room_id})

        if data:
            messages = [Message(**msg) for msg in data.get('messages', [])]
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

    def add_message(self, room_id: str, message: Message):
        message_dict = message.__dict__
        logger.info(f"Adding message to chatroom ID: {room_id} - Message: {message_dict}")

        result = self._collection.update_one(
            {"room_id": room_id},
            {"$push": {"messages": message_dict}}
        )

        if result.modified_count > 0:
            logger.info("Message added successfully.")
        else:
            logger.warning(f"Failed to add message to chatroom ID: {room_id}. Room may not exist.")

    def get_message_participants(self, message_id):
        data = self._collection.find_one({"_id": ObjectId(str(message_id))})
        if data:
            return {
                "recipient": data.get("recipient_id"),
                "sender": data.get("sender_id")
            }
        else:
            logger.warning(f"Message with ID {message_id} not found")
            return None
