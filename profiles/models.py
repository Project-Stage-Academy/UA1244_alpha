from django.db import models

from users.models import User


class StartUpProfile(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)  # model User is empty
    name = models.CharField(unique=True, max_length=255, blank=False)
    description = models.TextField()
    website = models.URLField(max_length=300, blank=True, null=True)
    startup_logo = models.ImageField(upload_to='startup_logos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Startup Profile"
        verbose_name_plural = "Startup Profiles"

    def __str__(self):
        return self.name
