from django.db import models

# Create your models here.
from startups.models import StartUpProfile
from investors.models import InvestorProfile


class InvestmentTracking(models.Model):
    investor_id = models.ForeignKey(InvestorProfile, on_delete = models.CASCADE)
    startup_id = models.ForeignKey(StartUpProfile, on_delete = models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add = True)

    class Meta:
        verbose_name = 'Investment Tracking'
        verbose_name_plural = 'Investment Tracking'
        ordering = ['-saved_at']

    def __str__(self):
        return f"Investor: {self.investor_id.__str__}, StartUp: {self.startup_id.__str__()}, saved at:{self.saved_at}"