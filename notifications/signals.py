from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import (
    StartUPTracking, 
    InvestorInitialMessage,
    NotificationType,
)
from .tasks import create_notification


@receiver(post_save, sender=StartUPTracking)
def create_notification_on_investor_follow(sender, instance, created, **kwargs):
    """Create a notification when an investor starts following a startup"""
    if created:
        create_notification.delay(
            investor_id=instance.investor.investor_id, 
            startup_id=instance.startup.startup_id,
            type_=NotificationType.FOLLOW
        )

@receiver(post_save, sender=InvestorInitialMessage)
def create_notification_on_investor_message(sender, instance, created, **kwargs):
    """Create a notification when an investor sends a message to a startup"""
    if created:
        create_notification.delay(
            investor_id=instance.investor.investor_id, 
            startup_id=instance.startup.startup_id,
            type_=NotificationType.MESSAGE,
            message_id=str(instance.message.id)
        )