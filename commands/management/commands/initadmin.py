import logging
import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError


User = get_user_model()
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        admin_username = os.getenv("ADMIN_USERNAME", "admin")
        admin_email = os.getenv("ADMIN_EMAIL", "admin@example.com")
        admin_password = os.getenv("ADMIN_PASSWORD", "admin")
        admin_first_name = os.getenv("ADMIN_FIRST_NAME", "admin")
        admin_last_name = os.getenv("ADMIN_LAST_NAME", "admin")

        if not User.objects.filter(username=admin_username).exists():
            logger.info("Creating admin account...")
            try:
                User.objects.create_superuser(
                    email=admin_email,
                    username=admin_username,
                    first_name=admin_first_name,
                    last_name=admin_last_name,
                    password=admin_password,
                )
                logger.info(f"Admin user '{admin_username}' created successfully.")
            except IntegrityError as e:
                logger.error(f"Failed to create admin user due to IntegrityError: {str(e)}")
            except Exception as e:
                logger.error(f"Unexpected error while creating admin user: {str(e)}")
        else:
            logger.info("Admin already initialized")
