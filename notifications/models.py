from uuid import uuid4

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


class Notification(models.Model):
    """Notification model
    
    Fields:
    - notification_id(UUID4Field)
    - notification_type(IntegerField): notification type (message/follow)
    - status(IntegerField): notification status (unread/read)
    - investor(ForeignKey): associated investor's id
    - startup(ForeignKey): associated startup's id
    - message_id(CharField): associated message id
    - created_at(DateTimeField)
    - sent_at(DateTimeField)
    - read_at(DateTimeField)
    """

    notification_id = models.UUIDField(
        primary_key=True, default=uuid4, editable=False)
    notification_type = models.IntegerChoices(choices=NotificationType.choices)
    status = models.IntegerChoices(
        choices=NotificationStatus.choices, default=NotificationStatus.UNREAD)
    investor = models.ForeignKey(InvestorProfile, on_delete=models.CASCADE)
    startup = models.ForeignKey(StartUpProfile, on_delete=models.CASCADE)
    message_id = models.CharField(max_length=24, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(blank=True, null=True)
    read_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f'{self.notification_type}: {self.investor} -> {self.startup}' \
        + f' {self.sent_at if self.sent_at else ""}'
    
    def retrieve_message(self):
        msg = None
        if self.message_id:
            try:
                msg = Message.objects.get(message_id=self.message_id)
            except Message.DoesNotExist:
                pass
        return msg             
         
    
class Message(models.Model): 
    pass
    
