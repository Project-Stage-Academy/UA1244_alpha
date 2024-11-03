import logging
from celery import shared_task

from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.utils import timezone

from forum.settings import DEFAULT_FROM_EMAIL
from .models import Notification, NotificationType


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
    except Exception as e:
        print(e)

@shared_task(bind=True, max_retries=3)
def send_notification_email(self, notification_id):
    """Send notification via email
    
    Parameters:
    - notification_id
    """
    notification = Notification.objects.get(id=notification_id)
    associated_profile_url = notification.get_associated_profile_url()
    startup = notification.startup.user_id
    startup_name = notification.startup.name
    investor = notification.investor.user

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
            message = f'Startup Profile [{startup_name}] you are following has new updates.'
            html_message = render_email_html_message(
                recipient, message, associated_profile_url, 'startup')

        case NotificationType.MESSAGE:
            return

    try:
        recipient_email = str(recipient)
        send_mail(subject=subject, message=message, from_email=DEFAULT_FROM_EMAIL,
                  recipient_list=[recipient_email], html_message=html_message,
                  fail_silently=False)
        notification.sent_at = timezone.now()
        notification.save()

    except Exception as e:
        logger.error('Error when sending notification email: {e}')
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
