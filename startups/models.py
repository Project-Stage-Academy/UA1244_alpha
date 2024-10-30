import logging

from django.contrib.auth import get_user_model
from django.db import models

from common.validators.image_validator import ImageValidator

User = get_user_model()
logger = logging.getLogger('django')


class StartUpProfile(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='startups')
    name = models.CharField(unique=True, max_length=255, blank=False)
    description = models.TextField()
    website = models.URLField(max_length=300, blank=True, null=True)
    startup_logo = models.ImageField(
        upload_to='startup_logos/',
        validators=[ImageValidator(max_size=5242880, max_width=1200, max_height=800)],
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.pk:
            logger.info(f"Updating StartupProfile: {self.name} (ID: {self.pk})")
        else:
            logger.info(f"Creating StartupProfile: {self.name}")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        logger.info(f"Deleting StartupProfile: {self.name} (ID: {self.pk})")
        super().delete(*args, **kwargs)


    class Meta:
        verbose_name = "Startup Profile"
        verbose_name_plural = "Startup Profiles"
        ordering = ['-created_at']

    def __str__(self) -> str:
        return self.name
