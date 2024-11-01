from django.db.models.signals import post_save
from django.dispatch import receiver

from investment_tracking.models import InvestmentTracking
from investors.models import InvestorProfile
from startups.models import StartUpProfile
from .models import (
    Notification,
    NotificationType,
)
from startups.models import StartUpProfile

from .tasks import (
    create_notification,
    send_notification_email,
    set_initial_notification_settings
)


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
        preferences = instance.get_notification_preferences()
        if preferences.get('email'):
            send_notification_email.delay(notification_id=instance.id)


@receiver(post_save, sender=StartUpProfile)
def create_notification_on_startup_update(sender, instance, **kwargs):
    """Create notifications for investor when startyp was updated"""

    tracking = InvestmentTracking.objects.filter(startup=instance)
    for track in tracking:
        create_notification.delay(
            investor_id=track.investor.id,
            startup_id=instance.id,
            type_=NotificationType.UPDATE
        )
        preferences = instance.get_notification_preferences()
        if preferences.get('email'):
            send_notification_email.delay(notification_id=instance.id)


@receiver(post_save, sender=InvestorProfile)
@receiver(post_save, sender=StartUpProfile)
def setup_notification_settings(sender, instance, created, **kwargs):
    if created:
        if sender == InvestorProfile:
            role_name = 'Investor'
        elif sender == StartUpProfile:
            role_name = 'Startup'
        else:
            raise ValueError('Invalid role')
        set_initial_notification_settings.delay(instance_id=instance.id, role_name=role_name)
