import logging
from django.db import models
from projects.models import Project
from investors.models import InvestorProfile

logger = logging.getLogger('django')

class TrackProjects(models.Model):
    """
    Model representing the tracking relationship between an investor and a project.
    
    Fields:
        - investor: ForeignKey to InvestorProfile, representing the investor tracking the project.
        - project: ForeignKey to Project, representing the project being tracked by the investor.
        - saved_at: DateTimeField automatically set to the time when the tracking record is created.
    
    Methods:
        - __str__: Returns a human-readable string representing the tracking relationship.
    """

    investor = models.ForeignKey(InvestorProfile, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Track Project'
        verbose_name_plural = 'Track Project'
        ordering = ['-saved_at']
        constraints = [
            models.UniqueConstraint(
                fields=['investor', 'project'],
                name='unique_investor_project'
            )
        ]

    def __str__(self):
        return f"Investor {self.investor}, Project {self.project}, Saved at {self.saved_at}"
