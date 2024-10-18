from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core import mail

import investment_tracking
from investors.models import InvestorProfile
from startups.models import StartUpProfile
from investment_tracking.models import InvestmentTracking
from .models import (
    Notification,
    NotificationType,
    NotificationStatus,
    NotificationDeliveryStatus,
)


User = get_user_model()


class NotificationTest(TestCase):
    """Test suite for the notification model"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        user_st = User.objects.create(
            email='user1@gmail.com', first_name='Startup', last_name='L', user_phone='+999999999')
        user_st.add_role('Startup')
        user_inv = User.objects.create(
            email='user2@gmail.com', first_name='Investor', last_name='L', user_phone='+999999999')
        user_inv.add_role('Investor')
        cls.investor_ = InvestorProfile.objects.create(user=user_inv)
        cls.startup_ = StartUpProfile.objects.create(
            user_id=user_st, name='Startup Company', description='')

    def test_investor_follow_notification(self):
        InvestmentTracking.objects.create(
            investor=self.investor_, startup=self.startup_)
        notification = Notification.objects.get(
            investor=self.investor_,
            startup=self.startup_
        )
        self.assertIsNotNone(notification)
        self.assertEqual(notification.notification_type, NotificationType.FOLLOW)

    def test_investor_follow_email_notification(self):
        InvestmentTracking.objects.create(
            investor=self.investor_, startup=self.startup_)
        notification = Notification.objects.get(
            investor=self.investor_,
            startup=self.startup_
        )
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, str(notification.startup.user_id))
        self.assertIn(notification.delivery_status, 
                      (NotificationDeliveryStatus.SENT,
                       NotificationDeliveryStatus.FAILED))
        if notification.delivery_status == NotificationDeliveryStatus.SENT:
            self.assertIsNotNone(notification.sent_at)
