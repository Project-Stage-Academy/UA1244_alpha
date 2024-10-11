from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from startups.models import StartUpProfile


class ProfileStartUpTests(APITestCase):

    def test_create_sturtup_profile(self):
        url = reverse('create')
        data = {'name': 'My first  startup',
                'description': 'this my first startup project, i want you to give me a lot of money:D',
                'website': 'www.firststartup.com',
                }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(StartUpProfile.objects.count(), 1)
        self.assertEqual(StartUpProfile.objects.get().name, 'DabApps')
