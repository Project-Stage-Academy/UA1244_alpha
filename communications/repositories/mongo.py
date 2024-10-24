from dataclasses import dataclass
from pymongo import MongoClient
from pymongo.errors import PyMongoError
import logging
from .base import AbstractRepository
from communications.entities.messages import (
    ChatRoom,
    Message
)

logger = logging.getLogger('django')

@dataclass
class MongoDBRepository(AbstractRepository):
    mongo_db_client: MongoClient
    mongo_db_db_name: str
    mongo_db_collection_name: str

    @property
    def _collection(self):
        return self.mongo_db_client[self.mongo_db_db_name][self.mongo_db_collection_name]

    def create_chatroom(self, chatroom: ChatRoom):
        chatroom_dict = chatroom.__dict__
        chatroom_dict['messages'] = [message.__dict__ for message in chatroom.messages]
        try:
            self._collection.insert_one(chatroom_dict)
            logger.info(f"ChatRoom {chatroom.room_id} was successfully created.")
        except PyMongoError as e:
            logger.error(f"Failed to create ChatRoom {chatroom.room_id}: {e}")

    def get_chatroom(self, room_id: str) -> ChatRoom:
        try:
            data = self._collection.find_one({"room_id": room_id})
            if data:
                messages = [Message(**msg) for msg in data.get('messages', [])]
                logger.info(f"ChatRoom {room_id} was retrieved from the database.")
                return ChatRoom(
                    room_id=data['room_id'],
                    startup_id=data.get('startup_id'),
                    investor_id=data.get('investor_id'),
                    messages=messages
                )
            logger.warning(f"ChatRoom {room_id} not found.")
        except PyMongoError as e:
            logger.error(f"Error retrieving ChatRoom {room_id}: {e}")
        return None

    def add_message(self, room_id: str, message: Message):
        message_dict = message.__dict__
        try:
            self._collection.update_one(
                {"room_id": room_id},
                {"$push": {"messages": message_dict}}
            )
            logger.info(f"Message added to ChatRoom {room_id}.")
        except PyMongoError as e:
            logger.error(f"Failed to add message to ChatRoom {room_id}: {e}")
