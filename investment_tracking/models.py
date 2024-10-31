import logging
from django.db import models
from startups.models import StartUpProfile
from investors.models import InvestorProfile

logger = logging.getLogger('django')


class InvestmentTracking(models.Model):
    """
    Model for tracking investments made by investors in startups.

    Attributes:
        investor (ForeignKey): The investor associated with the investment.
        startup (ForeignKey): The startup associated with the investment.
        saved_at (DateTimeField): The timestamp when the investment was recorded.

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
        return f"Investor: {self.investor}, StartUp: {self.startup}, saved at: {self.saved_at}"

    def save(self, *args, **kwargs):
        """
        Override the save method to add logging when an investment is saved.
        """
        logger.info(f"Saving investment tracking for Investor: {self.investor}, StartUp: {self.startup}.")
        try:
            super().save(*args, **kwargs)
            logger.info(
                f"Investment tracking saved successfully for Investor: {self.investor}, StartUp: {self.startup}.")
        except Exception as e:
            logger.error(
                f"Failed to save investment tracking for Investor: {self.investor}, StartUp: {self.startup}. Error: {e}")
            raise

    def delete(self, *args, **kwargs):
        """
        Override the delete method to add logging when an investment is deleted.
        """
        logger.info(f"Deleting investment tracking for Investor: {self.investor}, StartUp: {self.startup}.")
        try:
            super().delete(*args, **kwargs)
            logger.info(
                f"Investment tracking deleted successfully for Investor: {self.investor}, StartUp: {self.startup}.")
        except Exception as e:
            logger.error(
                f"Failed to delete investment tracking for Investor: {self.investor}, StartUp: {self.startup}. Error: {e}")
            raise
