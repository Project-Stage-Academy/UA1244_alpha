from rest_framework_simplejwt.tokens import RefreshToken
from users.models import User
from investors.models import InvestorProfile
from startups.models import StartUpProfile
from .models import InvestmentTracking
from django.db.utils import IntegrityError
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

class InvestmentTrackingTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="john@gmail.com",
            password="123456pok",
            first_name="John",
            last_name="Doe",
            user_phone="+1234567890")
        self.user.add_role('Investor')
        self.investor = InvestorProfile.objects.create(user=self.user)

        refresh = RefreshToken.for_user(self.user)
        access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)

        self.user_2 = User.objects.create_user(
            email="lin@gmail.com",
            password="123456pok",
            first_name="Lim",
            last_name="Non",
            user_phone="+1234567890"
        )
        self.user_2.add_role("Startup")

        self.startup1 = StartUpProfile.objects.create(
            user_id=self.user_2,
            name='Startup 1',
            description='Test dddd',
            website='www.strtas.com'
        )

        self.startup2 = StartUpProfile.objects.create(
            user_id=self.user_2,
            name='Startup 2',
            description='Test dddd2',
            website='www.strtas2.com'
        )

        self.startup3 = StartUpProfile.objects.create(
            user_id=self.user_2,
            name='Startup 3',
            description='Test dddd3',
            website='www.strtas3.com'
        )

    def test_save_to_investment_tracking(self):
        investment_tracking = InvestmentTracking.objects.create(
            investor=self.investor,
            startup=self.startup1)

        self.assertIsNotNone(investment_tracking.id)

    def test_add_to_investment_tracking(self):
        investment_tracking = InvestmentTracking.objects.create(
            investor=self.investor,
            startup=self.startup1)

        investment_tracking.startup = self.startup2
        investment_tracking.save()

        self.assertEqual(investment_tracking.startup, self.startup2)

    def test_investment_tracking_list(self):
        InvestmentTracking.objects.create(
            investor=self.investor,
            startup=self.startup1)

        InvestmentTracking.objects.create(
            investor=self.investor,
            startup=self.startup2)

        response = self.client.get(reverse('list-saved-startups'))

        print(response.data['results'])

        self.assertEqual(len(response.data['results']), 2)

        startup_ids = {startup['startup'] for startup in response.data['results']}
        expected_ids = {self.startup1.id, self.startup2.id}

        self.assertSetEqual(startup_ids, expected_ids)

    def test_unsave_from_investment_tracking(self):
        InvestmentTracking.objects.create(
            investor=self.investor,
            startup=self.startup1)

        InvestmentTracking.objects.create(
            investor=self.investor,
            startup=self.startup2)

        response = self.client.delete(reverse('unsave-followed-startups', args=[self.startup1.id]))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_investment_tracking_list_filtering(self):
        InvestmentTracking.objects.create(
            investor=self.investor,
            startup=self.startup1)

        InvestmentTracking.objects.create(
            investor=self.investor,
            startup=self.startup2)

        response = self.client.get(reverse('list-saved-startups'), {'startup__name': 'Startup 1'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_investment_tracking_list_sorting(self):
        InvestmentTracking.objects.create(
            investor=self.investor,
            startup=self.startup1)

        InvestmentTracking.objects.create(
            investor=self.investor,
            startup=self.startup2)

        InvestmentTracking.objects.create(
            investor=self.investor,
            startup=self.startup3)

        response = self.client.get(reverse('list-saved-startups'), {'ordering': 'startup__name'})
        print(response.data['results'])

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        startup_names = [startup['startup_name'] for startup in response.data['results']]
        expected_names = [self.startup1.name, self.startup2.name, self.startup3.name]
        self.assertEqual(startup_names, expected_names)

        response = self.client.get(reverse('list-saved-startups'), {'ordering': '-saved_at'})
        print(response.data['results'])

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_catch_exceptions(self):
        InvestmentTracking.objects.create(
            investor=self.investor,
            startup=self.startup3
        )

        try:
            InvestmentTracking.objects.create(
                investor=self.investor,
                startup=self.startup3
            )
        except IntegrityError:
            print('IntegrityError caught')
        else:
            print('No IntegrityError raised')
