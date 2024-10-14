from datetime import timedelta
from uuid import uuid4

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError

from simple_history.models import HistoricalRecords

from startups.models import StartUpProfile
from investors.models import InvestorProfile

# Create your models here.
class Project(models.Model):
    """Project model
    
    Fields:
    - project_id(UUIDField)
    - startup(ForeignKey): id of startup owning the project
    - investor(ManyToManyField): investors sponsoring the project
    - title(CharField): project name
    - risk(FloatField): project risk value (0.0 - 1.0)
    - description(TextField): project description
    - business_plan(URLField): URL link to business plan file
    - amount(DecimalField): finances needed
    - media_files(BinaryField): images, videos, etc.
    - status(IntegerField): project status choice field(seeking, in_progress, final_call, closed)
    - duration(DurationField): project duration
    - created_at(DateTimeField)
    - updated_at(DateTimeField
    - history: HistoricalRecords object for tracking updates"""

    class ProjectStatus(models.IntegerChoices):
        """IntegerChoices ProjectStatus class
        
        - SEEKING = 1: active, no investors yet
        - IN_PROGRESS = 2:  active, some investors involved
        - FINAL_CALL = 3: active, almost funded
        - CLOSED = 4: inactive"""

        SEEKING = 1
        IN_PROGRESS = 2
        FINAL_CALL = 3
        CLOSED = 4

    project_id = models.UUIDField(
        primary_key=True, default=uuid4, editable=False)
    startup = models.ForeignKey(
        StartUpProfile, related_name='projects', on_delete=models.CASCADE)
    investor = models.ManyToManyField(
        InvestorProfile, related_name='projects', blank=True, through="Subscription")
    title = models.CharField(max_length=255)
    risk = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    description = models.TextField()
    business_plan = models.URLField(blank=True, null=True)
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0.0)])
    media_files = models.BinaryField(blank=True, null=True)
    status = models.IntegerField(
        choices=ProjectStatus.choices, default=ProjectStatus.SEEKING)
    duration = models.DurationField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.title

    def clean_duration(self):
        if self.duration is not None and self.duration <= timedelta(0):
            raise ValidationError('Duration must be a positive value')


class Subscription(models.Model):
    """Subscription model for assigning investors to projects
    
    Fields:
    - investor(ForeignKey): investor id
    - project(ForeignKey): project id
    - contract_url(URLField): URL link to the contract file
    - share(FloatField): share funded by investor (0.0 - 1.0)
    - created_at(models.DateTimeField)"""
    investor = models.ForeignKey(InvestorProfile, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    contract_url = models.URLField()
    share = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)], null=True)
    created_at = models.DateTimeField(auto_now_add=True)
