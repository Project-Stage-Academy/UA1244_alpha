import logging
from dataclasses import dataclass

from channels.db import database_sync_to_async
from channels.layers import get_channel_layer

from communications.domain.entities.messages import Message, ChatRoom
from communications.events.base import BaseEvent

logger = logging.getLogger(__name__)


@dataclass
class MessageNotificationEvent(BaseEvent):
    async def trigger(self, message: Message, chat: ChatRoom):
        from notifications.models import Notification  
        try:
            await database_sync_to_async(Notification.objects.create)(
                investor_id=chat.receiver_id,
                startup_id=chat.sender_id,
                notification_type=2,
                message_id=message.oid
            )

            logger.info(f"Notification object created for message from sender {chat.receiver_id}")

            channel_layer = get_channel_layer()
            await channel_layer.group_send(
                f'notifications_{chat.receiver_id}',
                {
                    'type': 'send_notification',
                    'notification': f'New message: {message.content.as_generic_type()}',
                }
            )
        except Exception as e:
            logger.error(f"Failed to create Notification: {e}", exc_info=True)
        return
