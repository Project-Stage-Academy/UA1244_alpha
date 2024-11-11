import logging
from dataclasses import dataclass

from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from cryptography.fernet import Fernet
from django.conf import settings

from communications.domain.entities.messages import Message, ChatRoom
from communications.events.base import BaseEvent

logger = logging.getLogger(__name__)
cipher_suite = Fernet(settings.ENCRYPTION_KEY)


@dataclass
class MessageNotificationEvent(BaseEvent):
    async def trigger(self, message: Message, chat: ChatRoom):
        from notifications.models import Notification
        try:
            sync_to_async(Notification.objects.create)(
                notification_type=2,
                message_id=message.oid
            )

            logger.info(f"Notification object created for message from sender {chat.sender_id}")

            channel_layer = get_channel_layer()
            await channel_layer.group_send(
                f'notifications_{chat.receiver_id}',
                {
                    'type': 'send_notification',
                    'sender': f'From: {chat.sender_id}',
                    'notification':
                        f'New message: {cipher_suite.decrypt(message.content).decode()}',
                }
            )
        except Exception as e:
            logger.error(f"Failed to create Notification: {e}", exc_info=True)
        return
