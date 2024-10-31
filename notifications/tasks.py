from ast import Pass
import logging
from sqlite3 import IntegrityError
from celery import shared_task
from smtplib import SMTPException

from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.forms import ValidationError
from django.utils import timezone

from forum.settings import DEFAULT_FROM_EMAIL
from users.models import Role
from investors.models import InvestorProfile
from startups.models import StartUpProfile
from .models import (
    Notification,
    NotificationType,
    NotificationPreferences,
    RolesNotifications
)


User = get_user_model()
logger = logging.getLogger(__name__)


@shared_task
def create_notification(investor_id, startup_id, type_, message_id=None):
    """Create notification instance"""
    try:
        Notification.objects.create(
            notification_type=type_,
            investor_id=investor_id,
            startup_id=startup_id,
            message_id=message_id
        )
    except (ValidationError, IntegrityError) as e:
        logger.error(f'Error occured while creating notification\n{e}')

@shared_task(bind=True, max_retries=3)
def send_notification_email(self, notification_id):
    """Send notification via email
    
    Parameters:
    - notification_id
    """
    notification = Notification.objects.get(id=notification_id)
    associated_profile_url = notification.get_associated_profile_url()
    startup = notification.startup.get_user_id()
    investor = notification.investor.get_user_id()

    match notification.notification_type:
        case NotificationType.FOLLOW:
            recipient = startup
            subject = 'Forum: New Follower'
            message = 'Another investor has started following you.'
            html_message = render_email_html_message(
                recipient, message, associated_profile_url, 'investor')

        case NotificationType.UPDATE:
            recipient = investor
            subject = 'Forum: Startup Profile Update'
            message = f'Startup Profile [{startup.name}] you are following has new updates.'
            html_message = render_email_html_message(
                recipient, message, associated_profile_url, 'startup')

        case NotificationType.MESSAGE:
            recipient = notification.get_message_participants().get('receiver_id')

    try:
        recipient_email = str(recipient)
        send_mail(subject=subject, message=message, from_email=DEFAULT_FROM_EMAIL,
                  recipient_list=[recipient_email], html_message=html_message,
                  fail_silently=False)
        notification.sent_at = timezone.now()
        notification.save()

    except SMTPException as e:
        logger.error(f'Error when sending notification email: {e}')
        try:
            raise self.retry(exc=e, countdown=30)
        except self.MaxRetriesExceededError:
            notification.update_delivery_status(sent=False)
    else:
        notification.update_delivery_status(sent=True)


def render_email_html_message(recipient, message, profile_url, profile_type):
    """Render email html_message with custom
    
    Parameters:
    - recipient
    - message
    - profile_url
    - profile_type
    """
    html_message = f'''
    <p>Hello, {recipient.get_full_name()}</p>
    <p>{message}</p>
    <p><a href={profile_url}>View {profile_type}'s profile</a></p>
    <p>Thank you for choosing Forum!</p>
    '''
    return html_message


@shared_task
def set_initial_notification_settings(instance_id, role_name):
    try:
        role = Role.objects.get(name=role_name)
        if role_name == 'Startup':
            instance = StartUpProfile.objects.get(id=instance_id)
        elif role_name == 'Investor':
            instance = InvestorProfile.objects.get(id=instance_id)
    except (Role.DoesNotExist, InvestorProfile.DoesNotExist, StartUpProfile.DoesNotExist) as e:
        logger.error(f'{e}\nCreated {role_name} instance not found: {instance_id}')
    
    allowed_notifications = RolesNotifications.objects.filter(role=role)

    for notification in allowed_notifications:
        NotificationPreferences.objects.get_or_create(
            user=instance.user_id,
            role=role,
            notification_type=notification.notification_type
        )