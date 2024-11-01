from django.db.models.signals import post_save
from django.dispatch import receiver

from investment_tracking.models import InvestmentTracking
from track_projects.models import TrackProjects
from .models import (
    Notification,
    NotificationType,
)
from startups.models import StartUpProfile
from projects.models import Project

from .tasks import create_notification, send_notification_email


@receiver(post_save, sender=InvestmentTracking)
def create_notification_on_investor_follow_startup(sender, instance, created, **kwargs):
    """Create a notification when an investor starts following a startup"""
    if created:
        create_notification.delay(
            investor_id=instance.investor.id,
            startup_id=instance.startup.id,
            type_=NotificationType.FOLLOW
        )

@receiver(post_save, sender=TrackProjects)
def create_notification_on_investor_follow_project(sender, instance, created, **kwargs):
    """Create a notification when an investor starts following a project"""
    if created and hasattr(instance, 'project') and instance.project:
        create_notification.delay(
            investor_id=instance.investor.id,
            startup_id=instance.project.startup.id,
            project_id=instance.project.project_id,
            type_=NotificationType.FOLLOW
        )


@receiver(post_save, sender=Notification)
def send_notification(sender, instance, created, **kwargs):
    """Send an email when new notification created"""
    if created:
        send_notification_email.delay(notification_id=instance.id)


@receiver(post_save, sender=StartUpProfile)
def create_notification_on_startup_update(sender, instance, **kwargs):
    """Create notifications for investor when startup is updated"""
    tracking = InvestmentTracking.objects.filter(startup=instance)
    for track in tracking:
        create_notification.delay(
            investor_id=track.investor.id,
            startup_id=instance.id,
            type_=NotificationType.UPDATE
        )

@receiver(post_save, sender=Project)
def create_notification_on_project_update(sender, instance, **kwargs):
    """Create notifications for investor when project is updated"""
    tracking = TrackProjects.objects.filter(project=instance)
    for track in tracking:
        create_notification.delay(
            investor_id=track.investor.id,
            startup_id=instance.startup.id,
            project_id=instance.project_id,
            type_=NotificationType.UPDATE
        )