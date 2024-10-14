from time import sleep

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.contrib.auth import get_user_model

from investors.models import InvestorProfile
from startups.models import StartUpProfile
from .models import Project, Subscription


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

    def test_project_history(self):
        """test project history tracking"""
        project_upd = Project.objects.get(project_id=self.project.project_id)
        project_upd.status = 3
        project_upd.save()
        self.assertEqual(len(self.project.history.all()), 2)

    def test_subscription(self):
        """test assigning investor to a project"""
        self.project.investor.add(self.investor_)
        self.assertTrue(Subscription.objects.filter(
            project_id=self.project.project_id,
            investor_id=self.investor_.id).exists(),
            True)

    def tearDown(self):
        self.project.delete()
