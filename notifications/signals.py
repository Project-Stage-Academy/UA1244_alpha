from django.db.models.signals import post_save
from django.dispatch import receiver

from investment_tracking.models import InvestmentTracking
from .models import (
    Notification,
    NotificationType,
)
from .tasks import create_notification, send_notification_email


@receiver(post_save, sender=InvestmentTracking)
def create_notification_on_investor_follow(sender, instance, created, **kwargs):
    """Create a notification when an investor starts following a startup"""
    if created:
        create_notification.delay(
            investor_id=instance.investor.id,
            startup_id=instance.startup.id,
            type_=NotificationType.FOLLOW
        )

@receiver(post_save, sender=Notification)
def send_notification(sender, instance, created, **kwargs):
    """Send an email when new notification created"""
    if created:
        send_notification_email.delay(notification_id=instance.id)
