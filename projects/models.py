import logging
from datetime import timedelta
from uuid import uuid4

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError

from simple_history.models import HistoricalRecords

from startups.models import StartUpProfile
from investors.models import InvestorProfile


logger = logging.getLogger('django')


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
        logger.info(f"Attempting to change status of project {self.project_id} from {self.status} to {status}")
        if status not in dict(self.ProjectStatus.choices).keys():
            logger.error(f"Invalid status value: {status} for project {self.project_id}")
            raise ValidationError(f'''Invalid status value.
                Valid options: {self.ProjectStatus.choices}''')

        match self.status:

            case self.ProjectStatus.SEEKING:
                if not self.investors.all() and status in (
                            self.ProjectStatus.IN_PROGRESS,
                            self.ProjectStatus.FINAL_CALL):
                    logger.error(f"Cannot change status to {status} for project {self.project_id} without investors")
                    raise ValidationError(
                        f'Project without investors cannot be set to {status}'
                    )

            case self.ProjectStatus.IN_PROGRESS | self.ProjectStatus.FINAL_CALL:
                if self.investors.all() and status == self.ProjectStatus.SEEKING:
                    logger.error(f"Cannot revert project {self.project_id} to SEEKING status with investors")
                    raise ValidationError(
                        f'Project with investors cannot be set to {status}'
                    )

            case self.ProjectStatus.CLOSED:
                logger.error(f"Attempt to change status of closed project {self.project_id}")
                raise ValidationError(
                    'This project has already been closed.'
                )

        self.status = status
        logger.info(f"Status of project {self.project_id} successfully changed to {status}")
        self.clean()
        self.save()

    def clean_duration(self):
        if self.duration is not None and self.duration <= timedelta(0):
            logger.error(f"Invalid project duration for project {self.project_id}: {self.duration}")
            raise ValidationError('Duration must be a positive value')

    def clean(self):
        logger.info(f"Cleaning project {self.project_id}")
        self.clean_duration()
        result = super().clean()
        logger.info(f"Project {self.project_id} passed validation")
        return result

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
        logger.info(f"Validating media file {self.media_file.name} for project {self.project_id}")
        if self.media_file:
            if self.media_file.size == 0:
                logger.error(f"Invalid or empty file uploaded: {self.media_file.name}")
                raise ValidationError('Invalid or empty file.')
            if self.media_file.name.endswith(valid_extensions_video):
                if self.media_file.size > 1024 * 1024 * 1024:
                    logger.error(f"Video file size exceeds limit: {self.media_file.name}")
                    raise ValidationError('Video size exceeds 1GB limit.')
            elif self.media_file.name.endswith(valid_extensions_image):
                if self.media_file.size > 15 * 1024 * 1024:
                    logger.error(f"Image file size exceeds limit: {self.media_file.name}")
                    raise ValidationError('Image size exceeds 15MB limit.')
            else:
                logger.error(f"Invalid file extension: {self.media_file.name}")
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

    def save(self, *args, **kwargs):
        logger.info(
            f"Creating subscription for investor {self.investor.id} on project {self.project.id} with share {self.share}")
        super().save(*args, **kwargs)
        logger.info(f"Subscription created successfully for investor {self.investor.id} on project {self.project.id}")

    class Meta:
        unique_together = ('investor', 'project')
