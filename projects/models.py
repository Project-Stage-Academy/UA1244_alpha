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
    investors = models.ManyToManyField(
        InvestorProfile, related_name='projects', blank=True, through="Subscription")
    title = models.CharField(max_length=255)
    risk = models.FloatField(
        validators=[
            MinValueValidator(0.0, message='Risk cannot be a negative value'),
            MaxValueValidator(1.0, message='Risk cannot be higher than 1.0')
        ])
    description = models.TextField()
    business_plan = models.URLField(blank=True, null=True)
    amount = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0.0, message='Amount cannot be a negative value')])
    status = models.IntegerField(
        choices=ProjectStatus.choices, default=ProjectStatus.SEEKING)
    duration = models.DurationField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def change_status(self, status:int):
        """Change project status
        
        Valid transitions:
        - SEEKING > IN_PROGRESS, FINAL_CALL (unless no investors)
        - SEEKING > CLOSED
        - IN_PROGRESS, FINAL_CALL > CLOSED
        - IN_PROGRESS, FINAL_CALL > SEEKING (if no investors)
        """
        if status not in dict(self.ProjectStatus.choices).keys():
            raise ValidationError(f'''Invalid status value.
                Valid options: {self.ProjectStatus.choices}''')

        match self.status:

            case self.ProjectStatus.SEEKING:
                if not self.investors.all() and status in (
                            self.ProjectStatus.IN_PROGRESS,
                            self.ProjectStatus.FINAL_CALL):
                    raise ValidationError(
                        f'Project without investors cannot be set to {status}'
                    )

            case self.ProjectStatus.IN_PROGRESS | self.ProjectStatus.FINAL_CALL:
                if self.investors.all() and status == self.ProjectStatus.SEEKING:
                    raise ValidationError(
                        f'Project with investors cannot be set to {status}'
                    )

            case self.ProjectStatus.CLOSED:
                raise ValidationError(
                    'This project has already been closed.'
                )

        self.status = status
        self.clean()
        self.save()

    def clean_duration(self):
        if self.duration is not None and self.duration <= timedelta(0):
            raise ValidationError('Duration must be a positive value')

    def clean(self):
        self.clean_duration()
        return super().clean()

    def __str__(self):
        return self.title

class MediaFile(models.Model):
    """Media file model (video, images) for projects
    
    Fields:
    - project (ForeignKey): associated project id
    - media_file (FileField): media files (video / image)
    """

    project = models.ForeignKey(
        Project, related_name='media_files', on_delete=models.CASCADE)
    media_file = models.FileField(upload_to='project_files/')

    def clean_media_file(self):
        """validating media files size and extenstion
        
        - max video size (mp4): 1 GB
        - max image size (png, jpg, jpeg): 10 MB"""
        valid_extensions_video = ('.mp4',)
        valid_extensions_image = ('.png', '.jpg', '.jpeg')
        if self.media_file:
            if self.media_file.size == 0:
                raise ValidationError('Invalid or empty file.')
            if self.media_file.name.endswith(valid_extensions_video):
                if self.media_file.size > 1024 * 1024 * 1024:
                    raise ValidationError('Video size exceeds 1GB limit.')
            elif self.media_file.name.endswith(valid_extensions_image):
                if self.media_file.size > 15 * 1024 * 1024:
                    raise ValidationError('Image size exceeds 15MB limit.')
            else:
                raise ValidationError(f'''Invalid file extension.
                    Allowed formats: {valid_extensions_image}, {valid_extensions_video}''')

    def clean(self):
        self.clean_media_file()
        return super().clean()

    def __str__(self):
        return self.media_file.name


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

    class Meta:
        unique_together = ('investor', 'project')
