from celery import shared_task
import logging

from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.urls import reverse

from .models import Notification, NotificationType
from investors.models import InvestorProfile
from startups.models import StartUpProfile


User = get_user_model()
logger = logging.getLogger(__name__)


@shared_task
def create_notification(investor_id, startup_id, type_, message_id=None):
    investor = InvestorProfile.objects.get(investor_id=investor_id)
    startup = StartUpProfile.objects.get(startup_id=startup_id)
    Notification.objects.create(
        notification_type=type_,
        investor=investor, startup=startup,
        message_id=message_id
    )
    
@shared_task
def send_notification(notification:Notification, email=True, push=True):
    startup = notification.startup.user_id
    startupt_url = reverse('profile-by-id', args=[startup.startup_id])
    investor = notification.investor.user
    investor_url = ...

    match notification.notification_type:
        case NotificationType.FOLLOW:
            recipient = startup
            subject = 'Forum: New Follower'
            message = 'Another investor has started following you.'
            html_message = render_email_html_message(
                recipient, message, investor_url, 'investor')

        case NotificationType.UPDATE:
            recipient = investor
            subject = 'Forum: Startup Profile Update'
            message = f'Startup Profile [{startup.name}] you are following has new updates.'
            html_message = render_email_html_message(
                recipient, message, startupt_url, 'startup')

        case NotificationType.MESSAGE:
            pass            

    try:
        send_mail(
            subject=subject, 
            message=message, 
            recipient_list=[recipient],
            html_message=html_message
        )
    except Exception as e:
        logger.error(f'Error when sending notification email: {e}')


def render_email_html_message(recipient, message, profile_url, profile_type):
    html_message = f'''
    <p>Hello, {recipient.get_full_name()}</p>
    <p>{message}</p>
    <p><a href={profile_url}>View {profile_type}'s profile</a></p>
    <p>Thank you for choosing Forum!</p>
    '''
    return html_message