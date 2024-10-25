from dataclasses import dataclass

from django.conf import settings
from django.core.mail import send_mail

from communications.entities.messages import ChatRoom, Message
from communications.repositories.mongo import MongoDBRepository


@dataclass(frozen=True)
class CreateChatCommand:
    mongo_repo: MongoDBRepository

    def handle(self, chat_room: ChatRoom):
        self.mongo_repo.create_chatroom(chat_room)

        # TODO: Improve notifications in #40-5
        send_mail(
            subject=f"Chat Room '{chat_room.room_id}' Created",
            message=f"The chat room '{chat_room.room_id}' has been successfully created.",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[chat_room.investor_id]
        )


@dataclass(frozen=True)
class SendMessageCommand:
    mongo_repo: MongoDBRepository

    def handle(self, room_name: str, message: Message):
        self.mongo_repo.add_message(room_name, message)

        # TODO: Improve notifications in #40-5
        send_mail(
            subject=f"New Message in Chat Room '{room_name}'",
            message=f"You have received a new message from {message.sender_id} in chat room '{room_name}'.",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[message.receiver_id]
        )
