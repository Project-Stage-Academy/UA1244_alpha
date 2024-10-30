from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from common.validators.image_validator import ImageValidator

User = get_user_model()


class PreferredStageChoices(models.IntegerChoices):
    SEED = 1, _('Seed')
    EARLY_STAGE = 2, _('Early Stage')
    GROWTH_STAGE = 3, _('Growth Stage')


class InvestorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='investors')
    investor_logo = models.ImageField(
        upload_to='investor_logos/',
        validators=[ImageValidator(max_size=5242880, max_width=1200, max_height=800)],
        blank=True,
        null=True
    )
    preferred_stage = models.IntegerField(choices=PreferredStageChoices.choices, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"ID: {self.user.id}, Email: {self.user.email}, Stage: {self.get_preferred_stage_display()}"
    
    def get_user_id(self):
        return self.user

    class Meta:
        verbose_name = 'Investor Profile'
        verbose_name_plural = 'Investor Profiles'
        ordering = ['-created_at']
