from django.db import models
from startups.models import StartUpProfile
from investors.models import InvestorProfile


class InvestmentTracking(models.Model):
    """
    Model for tracking investments made by investors in startups.

    Attributes:
        investor (ForeignKey): The investor associated with the investment.
        startup (ForeignKey): The startup associated with the investment.
        saved_at (DateTimeField): The timestamp when the investment was recorded.

    Meta:
        unique constraint on (investor, startup) to prevent duplicate investments.

    Methods:
        __str__(): Returns a string representation of the investment tracking entry.
    """
     
    investor = models.ForeignKey(InvestorProfile, on_delete=models.CASCADE)
    startup = models.ForeignKey(StartUpProfile, on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Investment Tracking'
        verbose_name_plural = 'Investment Tracking'
        ordering = ['-saved_at']
        constraints = [
            models.UniqueConstraint(
                fields=["investor", "startup"],
                name="unique_investor_startup"
            )
        ]

    def __str__(self):
        return f"Investor: {self.investor}, StartUp: {self.startup}, saved at:{self.saved_at}"
