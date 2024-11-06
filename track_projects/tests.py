from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import TrackProjects
from projects.models import Project
from investors.models import InvestorProfile
from startups.models import StartUpProfile
from django.test import TestCase
from django.utils import timezone
from unittest.mock import patch

User = get_user_model()

class TrackProjectsModelTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user_st = User.objects.create(
            email='user1@gmail.com', first_name='Startup', last_name='St', user_phone='+999999999')
        cls.user_st.add_role('Startup')
        cls.user_inv = User.objects.create(
            email='user2@gmail.com', first_name='Investor', last_name='In', user_phone='+999999999')
        cls.user_inv.add_role('Investor')
        cls.investor = InvestorProfile.objects.create(user=cls.user_inv)
        cls.startup = StartUpProfile.objects.create(
            user_id=cls.user_st, name='Startup Company', description='')
    
    def setUp(self):
        self.project = Project.objects.create(
            startup=self.startup, title='Test pr', risk=0.2,
            description='...', business_plan='https://google2.com',
            amount=3049, status=1)

    
    def test_create_track_project(self):
        """Test creating a TrackProject instance."""
        track_project = TrackProjects.objects.create(
            project=self.project,
            investor=self.investor
        )
        self.assertIsInstance(track_project, TrackProjects)
        self.assertEqual(track_project.project, self.project)
        self.assertEqual(track_project.investor, self.investor)
    
    @patch('django.utils.timezone.now')
    def test_str_method(self, mock_now):
        """Test the string representation of the TrackProject instance."""

        fixed_time = timezone.datetime(2024, 11, 3, 12, 0, 0)
        mock_now.return_value = fixed_time

        track_project = TrackProjects.objects.create(
            project=self.project,
            investor=self.investor,
            saved_at=timezone.now()  
        )

        expected_str = f"Investor {self.investor}, Project {self.project}, Saved at {timezone.now()}"
        self.assertEqual(str(track_project), expected_str)

    def test_unique_project_investor(self):
        """Test that a TrackProject cannot be created with the same investor and project."""
        TrackProjects.objects.create(project=self.project, investor=self.investor)
        with self.assertRaises(Exception):
            TrackProjects.objects.create(project=self.project, investor=self.investor)

    def test_project_relation(self):
        """Test the relationship between TrackProjects and Project."""
        track_project = TrackProjects.objects.create(
            project=self.project,
            investor=self.investor
        )
        self.assertEqual(track_project.project.title, self.project.title)

    def test_investor_relation(self):
        """Test the relationship between TrackProjects and InvestorProfile."""
        track_project = TrackProjects.objects.create(
            project=self.project,
            investor=self.investor
        )
        self.assertEqual(track_project.investor.id, self.investor.id)


class TrackProjectFollowViewTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email="john@gmail.com",
            password="123456pok",
            first_name="John",
            last_name="Doe",
            user_phone="+1234567890"
        )
        cls.user.add_role("Investor")

        user_2 = User.objects.create_user(
            email="lin@gmail.com",
            password="123456pok",
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

    def setUp(self):
        self.project = Project.objects.create(
            startup=self.startup, title='Prj1', risk=0.5,
            description='...', business_plan='https://google.com',
            amount=10000, status=1)
        self.url = reverse('project-track', kwargs={'project_id': self.project.project_id})

        self.client = APIClient()
        token_url = reverse('token-create')
        response = self.client.post(token_url, {
            'email': 'john@gmail.com',
            'password': '123456pok',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def test_follow_project_success(self):
        response = self.client.post(self.url, data={},  format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('You successfully subscribed to project', response.data['message'])
        self.assertTrue(TrackProjects.objects.filter(investor=self.investor, project=self.project).exists())

    def test_follow_project_already_tracked(self):
        self.client.post(self.url, data={}, format='json')  
    
        response = self.client.post(self.url, data={}, format='json')  
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    

class InvestorsProjectsListViewTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
       
        cls.user = User.objects.create_user(
            email="john@gmail.com",
            password="123456pok",
            first_name="John",
            last_name="Doe",
            user_phone="+1234567890"
        )
        cls.user.add_role("Investor")

        cls.startup_user = User.objects.create_user(
            email="lin@gmail.com",
            password="123456pok",
            first_name="Lim",
            last_name="Non",
            user_phone="+1234567890"
        )
        cls.startup_user.add_role("Startup")

        cls.investor = InvestorProfile.objects.create(user=cls.user) 
        cls.startup = StartUpProfile.objects.create(
            user_id=cls.startup_user, 
            name='Startup 1',
            description='Test description',
            website='www.strtas.com'
        )

        cls.project = Project.objects.create(
            startup=cls.startup, title='Prj1', risk=0.5,
            description='Project description', business_plan='https://google.com',
            amount=10000, status=1)

        TrackProjects.objects.create(investor=cls.investor, project=cls.project)

    def setUp(self):
        self.client = APIClient()
        
        token_url = reverse('token-create')  
        response = self.client.post(token_url, {
            'email': 'john@gmail.com',
            'password': '123456pok',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        self.list_projects_url = reverse('track-project-list')

    def test_list_followed_projects(self):
        response = self.client.get(self.list_projects_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0) 