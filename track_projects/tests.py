from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import TrackProjects
from projects.models import Project
from investors.models import InvestorProfile
from startups.models import StartUpProfile

User = get_user_model()

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
        token_url = reverse('jwt-create')
        response = self.client.post(token_url, {
            'email': 'john@gmail.com',
            'password': '123456pok',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def test_follow_project_success(self):
        response = self.client.post(self.url, data={})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('You successfully subscribed to project', response.data['message'])
        self.assertTrue(TrackProjects.objects.filter(investor=self.investor, project=self.project).exists())

    def test_follow_project_already_tracked(self):
        self.client.post(self.url, data={})
        
        response = self.client.post(self.url, data={})
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
        
        token_url = reverse('jwt-create')  
        response = self.client.post(token_url, {
            'email': 'john@gmail.com',
            'password': '123456pok',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        self.list_projects_url = reverse('track-project-list')

    def test_list_followed_projects(self):
        response = self.client.get(self.list_projects_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0) 