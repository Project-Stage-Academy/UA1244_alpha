from dataclasses import dataclass
import logging
from typing import Optional


logger = logging.getLogger('memory_repo')


try:
    from communications.domain.entities.messages import ChatRoom
except ImportError as e:
    logger.error("Failed import BaseChatsRepository")


try:
    from communications.repositories.base import BaseChatsRepository
except ImportError as e:
    logger.error("Failed import BaseChatsRepository")


@dataclass
class MemoryChatRepositories(BaseChatsRepository):
    memory_data = {}

    def create_chatroom(self, chatroom: ChatRoom):
        try:
            self.memory_data[chatroom.oid] = chatroom.__dict__
        except Exception as e:
            logger.error(f"Trouble with creating new chat Error: {e}")

    def get_chatroom(self, room_oid: str) -> Optional[ChatRoom]:
        try:
            data = self.memory_data.get(room_oid)

            if not data:
                logger.warning(f"Data not found. Data: {data}")
                return False


            if isinstance(data, dict):
                chatroom = ChatRoom(
                    title=data['title'],
                    sender_id=data.get('sender_id'),
                    receiver_id=data.get('receiver_id'),
                    messages=data.get(data["messages"])
                )
                logger.info(f"Chatroom retrieved successfully: {chatroom}")
                return chatroom
    
            return False
        except Exception as e:
            logger.error(f"Something went wrong. Error: {e}")
