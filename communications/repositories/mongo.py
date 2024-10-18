from dataclasses import dataclass
from pymongo import MongoClient
from .base import AbstractRepository
from communications.entities.messages import (
    ChatRoom,
    Message
)


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
        self._collection.insert_one(chatroom_dict)

    def get_chatroom(self, room_id: str) -> ChatRoom:
        data = self._collection.find_one({"room_id": room_id})
        if data:
            messages = [Message(**msg) for msg in data.get('messages', [])]
            return ChatRoom(room_id=data['room_id'], participants=data['participants'], messages=messages)
        return None

    def add_message(self, room_id: str, message: Message):
        message_dict = message.__dict__
        self._collection.update_one(
            {"room_id": room_id},
            {"$push": {"messages": message_dict}}
        )
