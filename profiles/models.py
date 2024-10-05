from django.db import models

from users.models import Users


class StartUpProfile(models.Model):
    user_id = models.ForeignKey(Users, on_delete=models.CASCADE)  # model User is empty
    name = models.CharField(unique=True, max_length=255, blank=False)
    description = models.TextField()
    website = models.CharField(max_length=255, blank=True)
    startup_logo = models.BinaryField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
