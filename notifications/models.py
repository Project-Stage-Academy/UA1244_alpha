import logging

from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.contrib.auth import get_user_model

from forum.settings import SITE_URL
from startups.models import StartUpProfile
from investors.models import InvestorProfile
from users.models import Role
from communications import init_container, MongoDBRepository


User = get_user_model()
logger = logging.getLogger('django')

container = init_container()
mongo_container = container.resolve(MongoDBRepository)
from projects.models import Project


class NotificationType(models.IntegerChoices):
    """Notification type class (IntegerChoices)
    
    - FOLLOW: 1
    - MESSAGE: 2
    - UPDATE: 3
    """
    FOLLOW = 1, _('Follow')
    MESSAGE = 2, _('Message')
    UPDATE = 3, _('Update')


class NotificationStatus(models.IntegerChoices):
    """Notification status class (IntegerChoices)
    
    - UNREAD: 0
    - READ: 1
    """
    UNREAD = 0, _('Unread')
    READ = 1, _('Read')

class NotificationDeliveryStatus(models.IntegerChoices):
    """Notification delivary status class (IntegerChoices)
    
    - FAILED: 0
    - SENT: 1
    """
    FAILED = 0, _('Failed')
    SENT = 1, _('Sent')

class Notification(models.Model):
    """Notification model
    
    Fields:
    - notification_type(IntegerField): notification type (message/follow)
    - status(IntegerField): notification status (unread/read)
    - investor(ForeignKey): associated investor's id
    - startup(ForeignKey): associated startup's id
    - project(ForeignKey): associated project's id
    - message_id(CharField): associated message id
    - delivery_status(BooleanField): notification delivary status (sent/failed)
    - created_at(DateTimeField)
    - sent_at(DateTimeField)
    - read_at(DateTimeField)
    """

    notification_type = models.IntegerField(choices=NotificationType.choices)
    status = models.IntegerField(
        choices=NotificationStatus.choices, default=NotificationStatus.UNREAD)
    investor = models.ForeignKey(InvestorProfile, on_delete=models.CASCADE)
    startup = models.ForeignKey(StartUpProfile, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, blank=True, null=True, on_delete=models.CASCADE)
    message_id = models.CharField(max_length=24, blank=True, null=True)
    delivery_status = models.IntegerField(
         choices=NotificationDeliveryStatus, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(blank=True, null=True)
    read_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        type_ = NotificationType(self.notification_type).label
        if self.project:
            return f'{type_}: {self.investor} -> {self.project} {self.sent_at if self.sent_at else ""}'
        return f'{type_}: {self.investor} -> {self.startup}' \
        + f' {self.sent_at if self.sent_at else ""}'

    def set_read_status(self, read):
        """Set notification status to READ or UNREAD"""
        self.status = NotificationStatus.READ if read else NotificationStatus.UNREAD
        self.save()

    def set_read_at(self, clear_=False):
        """Set read_at to timezone.now() or None"""
        if clear_:
            self.read_at = None
        else:
            self.read_at = timezone.now()

    def update_delivery_status(self, sent=True):
        """Set notification delivery status to SENT or FAILED"""
        status = (NotificationDeliveryStatus.FAILED,
                  NotificationDeliveryStatus.SENT)[sent]
        self.delivery_status = status
        self.save()

    def get_associated_profile_url(self):
        """Get URL to associated profile depending on notification type"""
        startup = self.startup.user_id
        startupt_url = f'{SITE_URL}{reverse("startup-profile-by-id", args=[startup.id])}'
        investor = self.investor.user
        investor_url = f'{SITE_URL}{reverse("investor-profile-by-id", args=[investor.id])}'
        if self.project:
            project_url = f'{SITE_URL}{reverse("project-by-id", args=[self.project.project_id])}' 

        match self.notification_type:
            case NotificationType.FOLLOW:
                associated_url = investor_url
            case NotificationType.UPDATE:
                if self.project:
                    associated_url = project_url
                associated_url = startupt_url
            case NotificationType.MESSAGE:
                return None

        return associated_url

    def get_message_participants(self):
        return mongo_container.message_participants(self.message_id)

    def get_role_profile(self, role):
        """get startup or investor fields by role name"""
        profile_fields = {
            'Investor': 'investor',
            'Startup': 'startup'
        }
        profile = profile_fields.get(role)
        if role:
            return getattr(self, profile, None)
        raise AttributeError(f'No attribute found for this role: {role}')

    def get_notification_preferences(self):
        """check email and in_app preferences for a notification"""

        notification_preferences = {
            'email': True,
            'in_app': True
        }
        preferences = None
        try:
            roles = RolesNotifications.objects.filter(
                notification_type=self.notification_type)

            if roles.count() > 1 and self.notification_type == NotificationType.MESSAGE:
                if self.handle_message_preferences():
                    preferences = self.handle_message_preferences()

            elif roles.count() == 1:
                role = roles.first()
                role_name = Role.objects.get(id=role.role_id).name
                receiver_profile = self.get_role_profile(role_name)

                logger.error(role.role_id, receiver_profile, receiver_profile.get_user(),
                             Notification.notification_type)
                preferences = NotificationPreferences.objects.get(
                    user_id=receiver_profile.get_user(),
                    role=role.role_id,
                    notification_type=self.notification_type,
                )
        except (Notification.DoesNotExist, RolesNotifications.DoesNotExist,
                Role.DoesNotExist, NotificationPreferences.DoesNotExist) as e:
            logger.error(
                f'Notification or Role Notification or Role or Preferences object not found\n{e}')
        except AttributeError as e:
            logger.error(f'Invalid role {e}')

        if preferences:
            notification_preferences['email'] = preferences.email
            notification_preferences['in_app'] = preferences.in_app

        return notification_preferences

    def handle_message_preferences(self):
        """get preferences for message notifications"""
        preferences = None
        participants = self.get_message_participants()

        if participants:
            receiver_user_id = participants.get('receiver_id')

            try:
                receiver_user = User.objects.get(id=receiver_user_id)
                roles = receiver_user.roles.all()
                if roles.exists():
                    allowed_notifications = RolesNotifications.objects.filter(
                            notification_type=self.notification_type,
                            role__in=roles
                    )
                    if allowed_notifications.exists():
                        preferences = NotificationPreferences.get(
                            user_id=receiver_user_id,
                            notification_type=self.notification_type
                        )
            except User.DoesNotExist:
                logger.error(f'User with id {receiver_user_id} not found')

        return preferences


class RolesNotifications(models.Model):
    """Notification types allowed per Role

    Fields:
    - role (ForeignKey): role id
    - notification_type(IntegerField): notification type from NotificationType Integerchoices class
    
    Default (fixtures):
    - Startup: 1 (FOLLOW), 2 (MESSAGE)
    - Investor: 2 (MESSAGE), 3 (UPDATE)"""

    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    notification_type = models.IntegerField(choices=NotificationType.choices)

    class Meta:
        unique_together = ['role', 'notification_type']


class NotificationPreferences(models.Model):
    """Notification Preferences model

    Fields:
    - user (ForeignKey): user id
    - role (ForeignKey): role id
    - notification_type (IntegerField): notification type from NotificationType IntegerChoices class
    - email (BooleanField): email notifications enabled/disabled, default=True
    - in_app (BooleanField): in-app notifications enabled/disabled, default=True
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    notification_type = models.IntegerField(choices=NotificationType.choices)
    email = models.BooleanField(default=True)
    in_app = models.BooleanField(default=True)

    class Meta:
        unique_together = ['user', 'role', 'notification_type']

    def check_notification_type(self, notification_type):
        """check is notification type is allowed for profile"""
        allowed = RolesNotifications.objects.filter(
            role=self.role,
            notification_type=notification_type
        )
        return allowed.exists()
