from datetime import timedelta
from time import sleep

from django.core.exceptions import ValidationError
from rest_framework.test import APITestCase, APIClient
from django.test import TestCase

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
import uuid

from investors.models import InvestorProfile
from startups.models import StartUpProfile
from .models import Project, Subscription, MediaFile


User = get_user_model()

# class ProjectTest(TestCase):
#     """Test suite for the project model"""

#     @classmethod
#     def setUpClass(cls):
#         super().setUpClass()

#         cls.user_st = User.objects.create(
#             email='user1@gmail.com', first_name='Startup', last_name='L', user_phone='+999999999')
#         cls.user_st.add_role('Startup')
#         cls.user_inv = User.objects.create(
#             email='user2@gmail.com', first_name='Investor', last_name='L', user_phone='+999999999')
#         cls.user_inv.add_role('Investor')
#         cls.investor_ = InvestorProfile.objects.create(user=cls.user_inv)
#         cls.startup_ = StartUpProfile.objects.create(
#             user_id=cls.user_st, name='Startup Company', description='')

#     def setUp(self):
#         self.project = Project.objects.create(
#             startup=self.startup_, title='Prj1', risk=0.5,
#             description='...', business_plan='https://google.com',
#             amount=10000, status=1)

#     def test_create_project(self):
#         """test project creation"""
#         self.assertTrue(Project.objects.filter(project_id=self.project.project_id).exists())

#     def test_create_project_invalid_risk(self):
#         """test project creation with invalid risk value"""
#         project = Project(
#             startup=self.startup_, title='Prj1', risk=100,
#             description='...', business_plan='https://google.com', amount=10000, status=1)
#         with self.assertRaises(ValidationError):
#             project.full_clean()

#     def test_create_project_risk_0(self):
#         """test project creation with edge risk value: 0"""
#         project = Project(
#             startup=self.startup_, title='Prj1', risk=0,
#             description='...', business_plan='https://google.com', amount=10000, status=1)
#         try:
#             project.full_clean()
#         except ValidationError:
#             self.fail()

#     def test_create_project_risk_1(self):
#         """test project creation with edge risk value: 1"""
#         project = Project(
#             startup=self.startup_, title='Prj1', risk=1,
#             description='...', business_plan='https://google.com', amount=10000, status=1)
#         try:
#             project.full_clean()
#         except ValidationError:
#             self.fail()

#     def test_create_project_invalid_duration(self):
#         """test project creation with negative duration"""
#         neg_dur = timedelta(hours=-1)
#         project = Project(
#         startup=self.startup_, title='Prj1', risk=0.5, duration=neg_dur,
#         description='...', business_plan='url', amount=10000, status=1)
#         with self.assertRaises(ValidationError):
#             project.full_clean()

#     def test_create_project_blank_business_plan(self):
#         """test project creation with blank field for the business plan link"""
#         project = Project(
#             startup=self.startup_, title='Prj1', risk=0.5,
#             description='...', amount=10000, status=1)
#         try:
#             project.full_clean()
#         except ValidationError:
#             self.fail()

#     def test_create_project_invalid_url(self):
#         """test project creation with invalid url"""
#         project = Project(
#             startup=self.startup_, title='Prj1', risk=0.5,
#             description='...', business_plan='url', amount=10000, status=1)
#         with self.assertRaises(ValidationError):
#             project.full_clean()

#     def test_update_project_invalid_status(self):
#         """test project creation with invalid status"""
#         self.project.status = 90
#         with self.assertRaises(ValidationError):
#             self.project.full_clean()

#     def test_update_project(self):
#         """test project update"""
#         updated_at_init = self.project.updated_at
#         try:
#             project_upd = Project.objects.get(project_id=self.project.project_id)
#             project_upd.business_plan = 'https://url'
#             sleep(2)
#             project_upd.save()
#             self.assertGreater(project_upd.updated_at, updated_at_init)
#         except Project.DoesNotExist:
#             self.fail('project not found')


#     def test_change_project_status_1_2_no_investors(self):
#         """test change project status from SEEKING to IN_PROGRESS without investors"""
#         with self.assertRaises(ValidationError):
#             self.project.change_status(2)

#     def test_change_project_status_1_3_no_investors(self):
#         """test change project status from SEEKING to FINAL_CALL without investors"""
#         with self.assertRaises(ValidationError):
#             self.project.change_status(3)

#     def test_change_project_status_1_2_with_investors(self):
#         """test change project status from SEEKING to IN_PROGRESS with 1 investor"""
#         self.project.investors.add(self.investor_)
#         try:
#             self.project.change_status(2)
#         except ValidationError:
#             self.fail()

#     def test_change_project_status_1_3_with_investors(self):
#         """test change project status from SEEKING to FINAL_CALL with 1 investor"""
#         self.project.investors.add(self.investor_)
#         try:
#             self.project.change_status(3)
#         except ValidationError:
#             self.fail()

#     def test_change_project_status_1_4(self):
#         """test change project status from SEEKING to CLOSED"""
#         try:
#             self.project.change_status(4)
#         except ValidationError:
#             self.fail()

#     def test_change_project_status_2_4(self):
#         """test change project status from IN_PROGRESS to CLOSED"""
#         self.project.investors.add(self.investor_)
#         self.project.change_status(2)
#         try:
#             self.project.change_status(4)
#         except ValidationError:
#             self.fail()

#     def test_change_project_status_3_4(self):
#         """test change project status from FINAL_CALL to CLOSED"""
#         self.project.investors.add(self.investor_)
#         self.project.change_status(3)
#         try:
#             self.project.change_status(4)
#         except ValidationError:
#             self.fail()

#     def test_change_project_status_2_1_no_investors(self):
#         """test change project status from IN_PROGRESS to SEEKING without investors"""
#         self.project.investors.add(self.investor_)
#         self.project.change_status(2)
#         self.project.investors.remove(self.investor_)
#         try:
#             self.project.change_status(1)
#         except ValidationError:
#             self.fail()

#     def test_change_project_status_3_1_no_investors(self):
#         """test change project status from FINAL_CALL to SEEKING without investors"""
#         self.project.investors.add(self.investor_)
#         self.project.change_status(3)
#         self.project.investors.remove(self.investor_)
#         try:
#             self.project.change_status(1)
#         except ValidationError:
#             self.fail()

#     def test_change_project_status_2_1_with_investors(self):
#         """test change project status from IN_PROGRESS to SEEKING with 1 investor"""
#         self.project.investors.add(self.investor_)
#         self.project.change_status(2)
#         with self.assertRaises(ValidationError):
#             self.project.change_status(1)

#     def test_change_project_status_3_1_with_investors(self):
#         """test change project status from FINAL_CALL to SEEKING with 1 investor"""
#         self.project.investors.add(self.investor_)
#         self.project.change_status(3)
#         with self.assertRaises(ValidationError):
#             self.project.change_status(1)


#     def test_project_history(self):
#         """test project history tracking"""
#         project_upd = Project.objects.get(project_id=self.project.project_id)
#         project_upd.status = 3
#         project_upd.save()
#         self.assertEqual(len(self.project.history.all()), 2)

#     def test_subscription(self):
#         """test assigning investor to the project"""
#         self.project.investors.add(self.investor_)
#         self.assertTrue(Subscription.objects.filter(
#             project_id=self.project.project_id,
#             investor_id=self.investor_.id).exists()
#         )

#     def test_adding_media_file_image(self):
#         """test adding media file to the project"""
#         image_file = SimpleUploadedFile('image.png',
#                                         b'x' * (1 * 1024 * 1024),
#                                         content_type='image/png')
#         media_file = MediaFile(project=self.project, media_file=image_file)
#         media_file.clean()
#         media_file.save()
#         self.assertIn(media_file, self.project.media_files.all())

#     def test_adding_media_file_invalid(self):
#         """test adding invalid media file to the project"""
#         image_file = SimpleUploadedFile('image.png',
#                                         b'x' * (0 * 1024 * 1024),
#                                         content_type='image/pn00')
#         media_file = MediaFile(project=self.project, media_file=image_file)
#         with self.assertRaises(ValidationError):
#             media_file.clean()
#             media_file.save()
#         self.assertNotIn(media_file, self.project.media_files.all())


# class MediaFileTest(TestCase):
#     """Test suite for the mediafile model"""

#     @classmethod
#     def setUpClass(cls):
#         super().setUpClass()

#         user_st = User.objects.create(
#             email='user1@gmail.com', first_name='Startup', last_name='L', user_phone='+999999999')
#         user_st.add_role('Startup')
#         startup_ = StartUpProfile.objects.create(
#             user_id=user_st, name='Startup Company', description='')
#         cls.project = Project.objects.create(
#             startup=startup_, title='Prj1', risk=0.5,
#             description='...', amount=10000)

#     def test_upload_video_1gb(self):
#         """test uploading video with edge size value"""
#         video_file = SimpleUploadedFile('video.mp4',
#                                         b'x' * (1024 * 1024 * 1024),
#                                         content_type='video/mp4')
#         media_file = MediaFile(self.project.project_id, video_file)
#         try:

#             media_file.clean_media_file()
#         except ValidationError:
#             self.fail()

#     def test_upload_video_too_big(self):
#         """test uploading too big video"""
#         video_file = SimpleUploadedFile('video.mp4',
#                                         b'x' * (2 * 1024 * 1024 * 1024),
#                                         content_type='video/mp4')
#         media_file = MediaFile(project=self.project, media_file=video_file)
#         with self.assertRaises(ValidationError):
#             media_file.clean_media_file()

#     def test_upload_image_png(self):
#         """test uploading png image"""
#         image_file = SimpleUploadedFile('image.png',
#                                         b'x' * (10 * 1024 * 1024),
#                                         content_type='image/png')
#         media_file = MediaFile(project=self.project, media_file=image_file)
#         try:
#             media_file.clean_media_file()
#         except ValidationError:
#             self.fail()

#     def test_upload_image_jpg_too_big(self):
#         """test uploading too big image"""
#         image_file = SimpleUploadedFile('image.jpg',
#                                         b'x' * (16 * 1024 * 1024),
#                                         content_type='image/jpg')
#         media_file = MediaFile(project=self.project, media_file=image_file)
#         with self.assertRaises(ValidationError):
#             media_file.clean_media_file()


#     def test_upload_image_jpeg_0(self):
#         """test uploading image with invalid size (0)"""
#         image_file = SimpleUploadedFile('image.jpeg',
#                                         b'x' * (0 * 1024 * 1024),
#                                         content_type='image/jpeg')
#         media_file = MediaFile(project=self.project, media_file=image_file)
#         with self.assertRaises(ValidationError):
#             media_file.clean_media_file()

#     def test_upload_pdf(self):
#         """test uploading pdf (invalid extension)"""
#         pdf_file = SimpleUploadedFile('file.pdf',
#                                       b'content',
#                                       content_type='application/pdf')
#         media_file = MediaFile(project=self.project, media_file=pdf_file)
#         with self.assertRaises(ValidationError):
#             media_file.clean_media_file()


class ProjectsViewTest(APITestCase):
    """
    Test suite for Project views, including list, detail, create, and update functionalities.
    """

    @classmethod
    def setUpTestData(cls):

        cls.user = User.objects.create_user(
            email="john@gmail.com",
            password="StrongPass123!",
            first_name="John",
            last_name="Doe",
            user_phone="+1234567890"
        )
        cls.user.add_role("Investor")

        user_2 = User.objects.create_user(
            email="lin@gmail.com",
            password="StrongPass123!",
            first_name="Lim",
            last_name="Non",
            user_phone="+1234567890"
        )
        user_2.add_role("Startup")

        cls.investor = InvestorProfile.objects.create(user=cls.user) 
        cls.startup = StartUpProfile.objects.create(
            user_id=user_2, 
            name='Startup 1',
            description='Test dddd',
            website='www.strtas.com'
        )

        cls.project1 = Project.objects.create(
            startup=cls.startup, title='Prj1', risk=0.5,
            description='...', business_plan='https://google.com',
            amount=10000, status=1)
        cls.project2 = Project.objects.create(
            startup=cls.startup, title='Prj2', risk=0.3,
            description='...', business_plan='https://google.com',
            amount=10004, status=1)

        cls.url_get_list = reverse('project-list')
        cls.url_startup_project = reverse('startups-project', args=[cls.startup.id])
        cls.url_create_project = reverse('project-create')
        cls.url_update_project = reverse('update-project', args=[cls.project1.project_id])
        cls.url_get_by_id = reverse('project-by-id', args=[cls.project2.project_id])
        
        cls.new_project = {
        'startup': cls.startup.id, 
        'title': 'Test3', 
        'risk': 0.5,
        'description': '...',
        'business_plan': 'https://google.com',
        'amount': 10000, 
        'status': 1
        }
    
    def setUp(self):

        self.client = APIClient()
        token_url = reverse('token-create')
        response = self.client.post(token_url, {
        'email': 'lin@gmail.com',
        'password': 'StrongPass123!',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def test_get_projects(self):
        """
        Test that the API returns a list of all projects.
        """
        response = self.client.get(self.url_get_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
        results = response.data.get('results', [])
    
        self.assertEqual(len(results), 2) 
        self.assertEqual(results[0]['title'], self.project1.title)
        self.assertEqual(results[1]['title'], self.project2.title)
    
    def test_get_startup_projects(self):
        """
        Test that the API returns a list of projects for a specific startup.
        """
        response = self.client.get(self.url_get_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data.get('results', [])

        self.assertEqual(len(results), 2) 
        self.assertEqual(results[0]['title'], self.project1.title)
        self.assertEqual(results[1]['title'], self.project2.title)
    
    def test_get_startup_not_found(self):
        """
        Test that the API returns a 404 error for a non-existent startup.
        """
        url = reverse('startups-project', args=[999]) 
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_create_project(self):
        """
        Test that a startup can create a new project.
        """
        response = self.client.post(self.url_create_project, self.new_project, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], 'New project created successfully')
    
    def test_create_project_no_permission(self):
        """
        Test that a user without the 'Startup' role cannot create a project.
        """
        client = APIClient()
        token_url = reverse('token-create')
        response = client.post(token_url, {
        'email': 'john@gmail.com',
        'password': 'StrongPass123!',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        token = response.data['access']
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        response = client.post(self.url_create_project, self.new_project, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['error'], 'You do not have permission to create a new project.')
    
    def test_create_project_validation_error(self):
        """
        Test that invalid data in the project creation request returns a validation error.
        """
        new_project_error = {
        'startup': self.startup.id, 
        'title': 'Test3', 
        'risk': 0.5,
        'description': '...',
        'business_plan': 'https://google.com',
        'amount': 10000, 
        'status': 7  
        }

        response = self.client.post(self.url_create_project, new_project_error, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    

    def test_update_project(self):
        """
        Test that a startup can update an existing project.
        """
        response = self.client.put(self.url_update_project, self.new_project, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.project1.refresh_from_db()
        self.assertEqual(self.project1.title, 'Test3')

    def test_update_project_no_permission(self):
        """
        Test that a user without the 'Startup' role cannot update a project.
        """
        client = APIClient()
        token_url = reverse('token-create')
        response = client.post(token_url, {
        'email': 'john@gmail.com',
        'password': 'StrongPass123!',
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        token = response.data['access']
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        response = client.put(self.url_update_project,  self.new_project, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['error'], 'You do not have permission to update this project.')
    
    def test_get_project_by_id(self):
        """
        Test that the API returns the correct project by its ID.
        """
        response = self.client.get(self.url_get_by_id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.project2.title)

    def test_project_not_found(self):
        """
        Test that the API returns a 404 error for a non-existent project.
        """
        non_existent_project_id = str(uuid.uuid4())  
        response = self.client.get(reverse('project-by-id', args=[non_existent_project_id]))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)  
        self.assertEqual(response.data['error'], "This project doesn't exist")
