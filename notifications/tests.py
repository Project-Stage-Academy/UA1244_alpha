from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.core import mail

from forum.settings import TEST_EMAIL_1, TEST_EMAIL_2
from investors.models import InvestorProfile
from startups.models import StartUpProfile
from investment_tracking.models import InvestmentTracking
from .models import (
    Notification,
    NotificationType,
    NotificationDeliveryStatus,
)


User = get_user_model()

class NotificationTest(TestCase):
    """Test suite for the notification model"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        user_st = User.objects.create(
            email=TEST_EMAIL_1, first_name='Startup', last_name='L', user_phone='+999999999')
        user_st.add_role('Startup')
        user_inv = User.objects.create(
            email=TEST_EMAIL_2, first_name='Investor', last_name='L', user_phone='+999999999')
        user_inv.add_role('Investor')
        cls.investor_ = InvestorProfile.objects.create(user=user_inv)
        cls.startup_ = StartUpProfile.objects.create(
            user_id=user_st, name='Startup Company', description='')
        cls.startup2_ = StartUpProfile.objects.create(
            user_id=user_st, name='Startup Company 2', description='')
        cls.follow_i_s = InvestmentTracking.objects.create(
            investor=cls.investor_, startup=cls.startup2_)

    def test_investor_follow_notification(self):
        """test notification creation when investor starts following startup"""

        InvestmentTracking.objects.create(
            investor=self.investor_, startup=self.startup_)
        notification = Notification.objects.get(
            investor=self.investor_,
            startup=self.startup_
        )
        self.assertIsNotNone(notification)
        self.assertEqual(notification.notification_type, NotificationType.FOLLOW)

    def test_investor_follow_email_notification(self):
        """test sending email notification when investor starts following startup"""

        InvestmentTracking.objects.create(
            investor=self.investor_, startup=self.startup_)
        notification = Notification.objects.get(
            investor=self.investor_,
            startup=self.startup_
        )
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to[0], str(notification.startup.user_id))
        self.assertIn(notification.delivery_status,
                      (NotificationDeliveryStatus.SENT,
                       NotificationDeliveryStatus.FAILED))
        if notification.delivery_status == NotificationDeliveryStatus.SENT:
            self.assertIsNotNone(notification.sent_at)

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend')
    def test_investor_follow_email_notification_real(self):
        """test sending email notification when investor starts following startup with real email"""

        InvestmentTracking.objects.create(
            investor=self.investor_, startup=self.startup_)
        notification = Notification.objects.get(
            investor=self.investor_,
            startup=self.startup_
        )
        self.assertIn(notification.delivery_status,
                      (NotificationDeliveryStatus.SENT,
                       NotificationDeliveryStatus.FAILED))
        if notification.delivery_status == NotificationDeliveryStatus.SENT:
            self.assertIsNotNone(notification.sent_at)
    
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend')
    def test_investor_update_startup_email_notification_real(self):
        """test sending email notification when startups was updates with real email"""
        
        self.startup2_.name = "Test name 222"
        self.startup2_.save()

        notification = Notification.objects.filter(
            investor=self.investor_,
            startup=self.startup2_
            ).order_by('-created_at').first()
        
        self.assertIn(notification.delivery_status,
                      (NotificationDeliveryStatus.SENT,
                       NotificationDeliveryStatus.FAILED))
        if notification.delivery_status == NotificationDeliveryStatus.SENT:
            self.assertIsNotNone(notification.sent_at)