from django.db import models
from django.utils.translation import gettext_lazy as _

from startups.models import StartUpProfile
from investors.models import InvestorProfile


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
    message_id = models.CharField(max_length=24, blank=True, null=True)
    delivery_status = models.IntegerField(
         choices=NotificationDeliveryStatus, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(blank=True, null=True)
    read_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        type_ = NotificationType(self.notification_type).label
        return f'{type_}: {self.investor} -> {self.startup}' \
        + f' {self.sent_at if self.sent_at else ""}'

    def set_read_status(self):
        """Set notification status to READ"""
        self.status = NotificationStatus.READ
        self.save()

    def update_delivery_status(self, sent=True):
        """Set notification delivery status to SENT or FAILED"""
        status = (NotificationDeliveryStatus.FAILED,
                  NotificationDeliveryStatus.SENT)[sent]
        self.delivery_status = status
        self.save()
