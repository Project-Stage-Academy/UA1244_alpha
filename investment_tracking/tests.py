from django.test import TestCase
from users.models import User
from investors.models import InvestorProfile
from startups.models import StartUpProfile
from .models import InvestmentTracking
from django.db.utils import IntegrityError
from django.utils import timezone
from datetime import datetime


class TestInvestmentTracking(TestCase):

    @classmethod
    def setUpTestData(cls):
        
        user = User.objects.create_user(
            email="john@gmail.com",
            password="123456pok",
            first_name="John",
            last_name="Doe",
            user_phone="+1234567890"
        )
        user.add_role("Investor")

        user_2 = User.objects.create_user(
            email="lin@gmail.com",
            password="123456pok",
            first_name="Lim",
            last_name="Non",
            user_phone="+1234567890"
        )
        user_2.add_role("Startup")

        cls.investor = InvestorProfile.objects.create(user=user) 
        cls.startup = StartUpProfile.objects.create(
            user_id=user_2, 
            name='Startup 1',
            description='Test dddd',
            website='www.strtas.com'
        )

        cls.startup2 = StartUpProfile.objects.create(
            user_id=user_2, 
            name='Startup 2',
            description='Test dddd2',
            website='www.strtas2.com'
        )

        cls.startup3 = StartUpProfile.objects.create(
            user_id=user_2, 
            name='Startup 3',
            description='Test dddd3',
            website='www.strtas3.com'
        )

        cls.error_investment_tracking = InvestmentTracking.objects.create(
            investor=cls.investor,
            startup=cls.startup3
        )
  
    def test_create_investment_tracking(self):
        investment_tracking = InvestmentTracking.objects.create(
            investor=self.investor,
            startup=self.startup
        )
        self.assertIsNotNone(investment_tracking.id)

    def test_update_investment_tracking(self):
        investment_tracking = InvestmentTracking.objects.create(
            investor=self.investor,
            startup=self.startup
        )
        investment_tracking.startup = self.startup2
        investment_tracking.save()
        self.assertEqual(investment_tracking.startup, self.startup2)
    
    def test_catch_exceptions(self):
        with self.assertRaises(IntegrityError):
            investment_tracking = InvestmentTracking.objects.create(
            investor=self.investor,
            startup=self.startup3
        )
        
