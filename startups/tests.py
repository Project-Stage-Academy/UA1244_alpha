from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from startups.models import StartUpProfile


class StartUpFilterSearchTests(APITestCase):

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            email="john@gmail.com",
            password="123456pok",
            first_name="John",
            last_name="Doe",
            user_phone="+1234567890"
        )
        self.user.add_role("Investor")

        StartUpProfile.objects.create(user_id=self.user, name="Tech Solutions", description="Innovative tech startup")
        StartUpProfile.objects.create(user_id=self.user, name="Eco Start", description="Sustainable energy startup")
        StartUpProfile.objects.create(user_id=self.user, name="Foodie", description="Food delivery service startup")

        self.client = APIClient()

        self.authenticate_user()

    def authenticate_user(self):
        url = reverse('jwt-create')
        response = self.client.post(url, {
            'email': 'john@gmail.com',
            'password': '123456pok',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def test_filter_by_name(self):
        url = reverse('startup-list')
        response = self.client.get(url, {'name': 'Tech Solutions'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Tech Solutions')

    def test_search_by_description(self):
        url = reverse('startup-list')
        response = self.client.get(url, {'search': 'energy'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['description'], 'Sustainable energy startup')

    def test_search_by_partial_name(self):
        url = reverse('startup-list')
        response = self.client.get(url, {'search': 'Food'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Foodie')
