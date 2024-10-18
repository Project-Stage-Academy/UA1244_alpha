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
        response = self.client.get(url, {'name': 'tech solutions'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Tech Solutions')

        self.assertIn('count', response.data)
        self.assertEqual(response.data['count'], 1)
        self.assertIsNone(response.data['next'])
        self.assertIsNone(response.data['previous'])

    def test_search_by_description(self):
        url = reverse('startup-list')
        response = self.client.get(url, {'search': 'energy'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['description'], 'Sustainable energy startup')

        self.assertIn('count', response.data)
        self.assertEqual(response.data['count'], 1)
        self.assertIsNone(response.data['next'])
        self.assertIsNone(response.data['previous'])

    def test_search_by_partial_name(self):
        url = reverse('startup-list')
        response = self.client.get(url, {'search': 'Food'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Foodie')

        self.assertIn('count', response.data)
        self.assertEqual(response.data['count'], 1)
        self.assertIsNone(response.data['next'])
        self.assertIsNone(response.data['previous'])

    def test_filter_with_no_matching_results(self):
        url = reverse('startup-list')
        response = self.client.get(url, {'name': 'Something'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)

        self.assertIn('count', response.data)
        self.assertEqual(response.data['count'], 0)
        self.assertIsNone(response.data['next'])
        self.assertIsNone(response.data['previous'])

    def test_invalid_search_query_handling(self):
        url = reverse('startup-list')
        response = self.client.get(url, {'search': 'fdghgfdhgfdhfgdhdfgh'})

        self.assertEqual(len(response.data['results']), 0)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
