import logging
from dataclasses import dataclass

from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer

from communications.entities.messages import Message
from communications.events.base import BaseEvent


logger = logging.getLogger(__name__)

@dataclass
class MessageNotificationEvent(BaseEvent):
    async def trigger(self, message: Message):
        from notifications.models import Notification  # Import delayed
        try:
            await database_sync_to_async(Notification.objects.create)(
                investor_id=message.sender_id,
                startup_id=message.receiver_id,
            )

            channel_layer = get_channel_layer()
            await channel_layer.group_send(
                f'notifications_{message.receiver_id}',
                {
                    'type': 'send_notification',
                    'notification': f'New message: {message.content}',
                }
            )
            logger.info(f"Notification sent to user {message.receiver_id}")
        except Exception as e:
            logger.error(f"Failed to create and send notification: {e}", exc_info=True)
