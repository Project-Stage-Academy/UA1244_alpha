import logging
from smtplib import SMTPException
from celery import shared_task

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
    except (ValidationError) as e:
        logger.error(f'Error occured while creating notification: {e}')

@shared_task(bind=True, max_retries=3)
def send_notification_email(self, notification_id):
    """Send notification via email
    
    Parameters:
    - notification_id
    """
    notification = Notification.objects.get(id=notification_id)
    associated_profile_url = notification.get_associated_profile_url()
    startup = notification.startup.get_user()
    investor = notification.investor.get_user()
    recipient = None

    match notification.notification_type:
        case NotificationType.FOLLOW:
            recipient = startup
            subject = 'Forum: New Follower'
            message = 'A new investor has started following you.'
            html_message = render_email_html_message(
                recipient, message, associated_profile_url, 'investor')

        case NotificationType.UPDATE:
            recipient = investor
            subject = 'Forum: Startup Profile Update'
            message = f'The startup [{notification.startup.name}] ' \
                + 'you are following has new updates.'
            html_message = render_email_html_message(
                recipient, message, associated_profile_url, 'startup')

        case NotificationType.MESSAGE:
            if notification.message_id:
                print(notification_id, notification.get_message_participants())
                participants = notification.get_message_participants()
                if participants:
                    recipient.get('receiver_id')
                    subject = 'Forum: New Message'
                    message = f'You have new message.'
                    html_message = render_email_html_message(
                        recipient, message, profile_url=None, profile_type=None, include_link=False)
                else:
                    logger.error('Failed to get message participants')
            else:
                logger.error('Invalid message_id')

    try:
        if recipient:
            recipient_email = recipient.email
            send_mail(subject=subject, message=message, from_email=DEFAULT_FROM_EMAIL,
                    recipient_list=[recipient_email], html_message=html_message,
                    fail_silently=False)
            notification.sent_at = timezone.now()
            notification.save()
        else:
            logger.error('Error fetching recipient')

    except SMTPException as e:
        logger.error(f'Error when sending notification email: {e}')
        try:
            raise self.retry(exc=e, countdown=30)
        except self.MaxRetriesExceededError:
            notification.update_delivery_status(sent=False)
    else:
        notification.update_delivery_status(sent=True)


def render_email_html_message(recipient, message, profile_url, profile_type, include_link=True):
    """Render email html_message with custom
    
    Parameters:
    - recipient
    - message
    - profile_url
    - profile_type
    """
    link_to_profile = f"<p><a href={profile_url}>View {profile_type}'s profile</a></p>"
    html_message = f'''
    <p>Hello, {recipient.get_full_name()}</p>
    <p>{message}</p>
    {link_to_profile if include_link else ''}
    <p>Thank you for choosing Forum!</p>
    '''
    return html_message


@shared_task
def set_initial_notification_settings(instance_id, role_name):
    """set initial notification settings for new profile
    
    Fields:
    - instance_id
    - role_name
    """
    instance = None
    try:
        role = Role.objects.get(name=role_name)
        if role_name == 'Startup':
            instance = StartUpProfile.objects.get(id=instance_id)
        elif role_name == 'Investor':
            instance = InvestorProfile.objects.get(id=instance_id)
    except (Role.DoesNotExist, InvestorProfile.DoesNotExist, StartUpProfile.DoesNotExist) as e:
        logger.error(f'{e} Created {role_name} instance not found: {instance_id}')

    allowed_notifications = RolesNotifications.objects.filter(role=role)

    if instance:
        for notification in allowed_notifications:
            NotificationPreferences.objects.get_or_create(
                user=instance.get_user(),
                role=role,
                notification_type=notification.notification_type
            )
