from celery import shared_task

from .models import Notification
from investors.models import InvestorProfile
from startups.models import StartUpProfile


@shared_task
def create_notification(investor_id, startup_id, type_, message_id=None):
    investor = InvestorProfile.objects.get(investor_id=investor_id)
    startup = StartUpProfile.objects.get(startup_id=startup_id)
    Notification.objects.create(
        notification_type=type_,
        investor=investor, startup=startup,
        message_id=message_id
    )
    
