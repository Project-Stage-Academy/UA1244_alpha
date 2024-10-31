import logging
from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import InvestorProfile


logger = logging.getLogger('django')

@receiver(post_delete, sender=InvestorProfile)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """Deletes file from filesystem when corresponding `InvestorProfile` object is deleted."""
    if instance.investor_logo:
        file_path = instance.investor_logo.path
        instance.investor_logo.delete(save=False)
        logger.info(f"Deleted investor logo at {file_path} for investor {instance.user.email}")
