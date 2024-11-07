import logging

from celery import shared_task
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.utils import timezone

from communications.di_container import init_container
from communications.repositories.base import BaseMessagesRepository
from forum.settings import DEFAULT_FROM_EMAIL
from investors.models import InvestorProfile
from startups.models import StartUpProfile
from users.models import Role
from .models import Notification, NotificationType, NotificationPreferences, RolesNotifications

User = get_user_model()
logger = logging.getLogger(__name__)

container = init_container()
mongo_repo: BaseMessagesRepository = container.resolve(BaseMessagesRepository)

@shared_task
def create_notification(investor_id, startup_id, type_, message_id=None, project_id=None):
    """Create notification instance"""
    try:
        Notification.objects.create(
            notification_type=type_,
            investor_id=investor_id,
            startup_id=startup_id,
            project_id=project_id,
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

    startup = notification.startup.get_user()
    investor = notification.investor.get_user()
    recipient = None
    startup = notification.startup.user_id
    startup_name = notification.startup.name
    investor = notification.investor.user
    project = None
    if notification.project:
        project = notification.project.startup.user_id
        project_title = notification.project.title

    match notification.notification_type:
        case NotificationType.FOLLOW:
            recipient = startup
            subject = 'Forum: New Follower'
            message = 'Another investor has started following you.'
            html_message = render_email_html_message(
                recipient, message, associated_profile_url, 'investor')
            if project:
                recipient = project
                subject = 'Forum: New Follower'
                message = 'Another investor has started following your project.'
                html_message = render_email_html_message(
                    recipient, message, associated_profile_url, 'investor')
            else:
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
            if project:
                recipient = investor
                subject = 'Forum: Project Update'
                message = f'Project [{project_title}] you are following has new updates.'
                html_message = render_email_html_message(
                    recipient, message, associated_profile_url, 'project')
            else:
                recipient = investor
                subject = 'Forum: Startup Profile Update'
                message = f'Startup Profile [{startup_name}] you are following has new updates.'
                html_message = render_email_html_message(
                    recipient, message, associated_profile_url, 'startup')

        case NotificationType.MESSAGE:
            message = mongo_repo.get_message_by_id(notification.message_id)
            receiver = User.objects.get(id=message.receiver_id)
            recipient = receiver.email
            subject = 'Forum: New message'
            message = 'You have a new message'
            html_message = render_email_html_message(
                recipient, message, associated_profile_url, 'startup')

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
    <p>Hello, {recipient}</p>
    <p>{message}</p>
    <p><a href={profile_url}>View {profile_type}'s profile</a></p>
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