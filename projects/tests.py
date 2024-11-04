from datetime import timedelta
from time import sleep

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from investors.models import InvestorProfile
from startups.models import StartUpProfile
from .models import Project, Subscription, MediaFile


User = get_user_model()

class ProjectTest(TestCase):
    """Test suite for the project model"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user_st = User.objects.create(
            email='user1@gmail.com', first_name='Startup', last_name='L', user_phone='+999999999')
        cls.user_st.add_role('Startup')
        cls.user_inv = User.objects.create(
            email='user2@gmail.com', first_name='Investor', last_name='L', user_phone='+999999999')
        cls.user_inv.add_role('Investor')
        cls.investor_ = InvestorProfile.objects.create(user=cls.user_inv)
        cls.startup_ = StartUpProfile.objects.create(
            user_id=cls.user_st, name='Startup Company', description='')

    def setUp(self):
        self.project = Project.objects.create(
            startup=self.startup_, title='Prj1', risk=0.5,
            description='...', business_plan='https://google.com',
            amount=10000, status=1)

    def test_create_project(self):
        """test project creation"""
        self.assertTrue(Project.objects.filter(project_id=self.project.project_id).exists())

    def test_create_project_invalid_risk(self):
        """test project creation with invalid risk value"""
        project = Project(
            startup=self.startup_, title='Prj1', risk=100,
            description='...', business_plan='https://google.com', amount=10000, status=1)
        with self.assertRaises(ValidationError):
            project.full_clean()

    def test_create_project_risk_0(self):
        """test project creation with edge risk value: 0"""
        project = Project(
            startup=self.startup_, title='Prj1', risk=0,
            description='...', business_plan='https://google.com', amount=10000, status=1)
        try:
            project.full_clean()
        except ValidationError:
            self.fail()

    def test_create_project_risk_1(self):
        """test project creation with edge risk value: 1"""
        project = Project(
            startup=self.startup_, title='Prj1', risk=1,
            description='...', business_plan='https://google.com', amount=10000, status=1)
        try:
            project.full_clean()
        except ValidationError:
            self.fail()

    def test_create_project_invalid_duration(self):
        """test project creation with negative duration"""
        neg_dur = timedelta(hours=-1)
        project = Project(
        startup=self.startup_, title='Prj1', risk=0.5, duration=neg_dur,
        description='...', business_plan='url', amount=10000, status=1)
        with self.assertRaises(ValidationError):
            project.full_clean()

    def test_create_project_blank_business_plan(self):
        """test project creation with blank field for the business plan link"""
        project = Project(
            startup=self.startup_, title='Prj1', risk=0.5,
            description='...', amount=10000, status=1)
        try:
            project.full_clean()
        except ValidationError:
            self.fail()

    def test_create_project_invalid_url(self):
        """test project creation with invalid url"""
        project = Project(
            startup=self.startup_, title='Prj1', risk=0.5,
            description='...', business_plan='url', amount=10000, status=1)
        with self.assertRaises(ValidationError):
            project.full_clean()

    def test_update_project_invalid_status(self):
        """test project creation with invalid status"""
        self.project.status = 90
        with self.assertRaises(ValidationError):
            self.project.full_clean()

    def test_update_project(self):
        """test project update"""
        updated_at_init = self.project.updated_at
        try:
            project_upd = Project.objects.get(project_id=self.project.project_id)
            project_upd.business_plan = 'https://url'
            sleep(2)
            project_upd.save()
            self.assertGreater(project_upd.updated_at, updated_at_init)
        except Project.DoesNotExist:
            self.fail('project not found')


    def test_change_project_status_1_2_no_investors(self):
        """test change project status from SEEKING to IN_PROGRESS without investors"""
        with self.assertRaises(ValidationError):
            self.project.change_status(2)

    def test_change_project_status_1_3_no_investors(self):
        """test change project status from SEEKING to FINAL_CALL without investors"""
        with self.assertRaises(ValidationError):
            self.project.change_status(3)

    def test_change_project_status_1_2_with_investors(self):
        """test change project status from SEEKING to IN_PROGRESS with 1 investor"""
        self.project.investors.add(self.investor_)
        try:
            self.project.change_status(2)
        except ValidationError:
            self.fail()

    def test_change_project_status_1_3_with_investors(self):
        """test change project status from SEEKING to FINAL_CALL with 1 investor"""
        self.project.investors.add(self.investor_)
        try:
            self.project.change_status(3)
        except ValidationError:
            self.fail()

    def test_change_project_status_1_4(self):
        """test change project status from SEEKING to CLOSED"""
        try:
            self.project.change_status(4)
        except ValidationError:
            self.fail()

    def test_change_project_status_2_4(self):
        """test change project status from IN_PROGRESS to CLOSED"""
        self.project.investors.add(self.investor_)
        self.project.change_status(2)
        try:
            self.project.change_status(4)
        except ValidationError:
            self.fail()

    def test_change_project_status_3_4(self):
        """test change project status from FINAL_CALL to CLOSED"""
        self.project.investors.add(self.investor_)
        self.project.change_status(3)
        try:
            self.project.change_status(4)
        except ValidationError:
            self.fail()

    def test_change_project_status_2_1_no_investors(self):
        """test change project status from IN_PROGRESS to SEEKING without investors"""
        self.project.investors.add(self.investor_)
        self.project.change_status(2)
        self.project.investors.remove(self.investor_)
        try:
            self.project.change_status(1)
        except ValidationError:
            self.fail()

    def test_change_project_status_3_1_no_investors(self):
        """test change project status from FINAL_CALL to SEEKING without investors"""
        self.project.investors.add(self.investor_)
        self.project.change_status(3)
        self.project.investors.remove(self.investor_)
        try:
            self.project.change_status(1)
        except ValidationError:
            self.fail()

    def test_change_project_status_2_1_with_investors(self):
        """test change project status from IN_PROGRESS to SEEKING with 1 investor"""
        self.project.investors.add(self.investor_)
        self.project.change_status(2)
        with self.assertRaises(ValidationError):
            self.project.change_status(1)

    def test_change_project_status_3_1_with_investors(self):
        """test change project status from FINAL_CALL to SEEKING with 1 investor"""
        self.project.investors.add(self.investor_)
        self.project.change_status(3)
        with self.assertRaises(ValidationError):
            self.project.change_status(1)


    def test_project_history(self):
        """test project history tracking"""
        project_upd = Project.objects.get(project_id=self.project.project_id)
        project_upd.status = 3
        project_upd.save()
        self.assertEqual(len(self.project.history.all()), 2)

    def test_subscription(self):
        """test assigning investor to the project"""
        self.project.investors.add(self.investor_)
        self.assertTrue(Subscription.objects.filter(
            project_id=self.project.project_id,
            receiver_id=self.investor_.id).exists()
        )

    def test_adding_media_file_image(self):
        """test adding media file to the project"""
        image_file = SimpleUploadedFile('image.png',
                                        b'x' * (1 * 1024 * 1024),
                                        content_type='image/png')
        media_file = MediaFile(project=self.project, media_file=image_file)
        media_file.clean()
        media_file.save()
        self.assertIn(media_file, self.project.media_files.all())

    def test_adding_media_file_invalid(self):
        """test adding invalid media file to the project"""
        image_file = SimpleUploadedFile('image.png',
                                        b'x' * (0 * 1024 * 1024),
                                        content_type='image/pn00')
        media_file = MediaFile(project=self.project, media_file=image_file)
        with self.assertRaises(ValidationError):
            media_file.clean()
            media_file.save()
        self.assertNotIn(media_file, self.project.media_files.all())


class MediaFileTest(TestCase):
    """Test suite for the mediafile model"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        user_st = User.objects.create(
            email='user1@gmail.com', first_name='Startup', last_name='L', user_phone='+999999999')
        user_st.add_role('Startup')
        startup_ = StartUpProfile.objects.create(
            user_id=user_st, name='Startup Company', description='')
        cls.project = Project.objects.create(
            startup=startup_, title='Prj1', risk=0.5,
            description='...', amount=10000)

    def test_upload_video_1gb(self):
        """test uploading video with edge size value"""
        video_file = SimpleUploadedFile('video.mp4',
                                        b'x' * (1024 * 1024 * 1024),
                                        content_type='video/mp4')
        media_file = MediaFile(self.project.project_id, video_file)
        try:

            media_file.clean_media_file()
        except ValidationError:
            self.fail()

    def test_upload_video_too_big(self):
        """test uploading too big video"""
        video_file = SimpleUploadedFile('video.mp4',
                                        b'x' * (2 * 1024 * 1024 * 1024),
                                        content_type='video/mp4')
        media_file = MediaFile(project=self.project, media_file=video_file)
        with self.assertRaises(ValidationError):
            media_file.clean_media_file()

    def test_upload_image_png(self):
        """test uploading png image"""
        image_file = SimpleUploadedFile('image.png',
                                        b'x' * (10 * 1024 * 1024),
                                        content_type='image/png')
        media_file = MediaFile(project=self.project, media_file=image_file)
        try:
            media_file.clean_media_file()
        except ValidationError:
            self.fail()

    def test_upload_image_jpg_too_big(self):
        """test uploading too big image"""
        image_file = SimpleUploadedFile('image.jpg',
                                        b'x' * (16 * 1024 * 1024),
                                        content_type='image/jpg')
        media_file = MediaFile(project=self.project, media_file=image_file)
        with self.assertRaises(ValidationError):
            media_file.clean_media_file()


    def test_upload_image_jpeg_0(self):
        """test uploading image with invalid size (0)"""
        image_file = SimpleUploadedFile('image.jpeg',
                                        b'x' * (0 * 1024 * 1024),
                                        content_type='image/jpeg')
        media_file = MediaFile(project=self.project, media_file=image_file)
        with self.assertRaises(ValidationError):
            media_file.clean_media_file()

    def test_upload_pdf(self):
        """test uploading pdf (invalid extension)"""
        pdf_file = SimpleUploadedFile('file.pdf',
                                      b'content',
                                      content_type='application/pdf')
        media_file = MediaFile(project=self.project, media_file=pdf_file)
        with self.assertRaises(ValidationError):
            media_file.clean_media_file()
