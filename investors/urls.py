from django.urls import path

from notifications.views import (
    ProfileNotificationSettingsView,
    ProfileNotificationSettingsByIDView,
    ProfileNotificationsListView
)
from .views import (
    InvestorProfileViewById, 
    InvestorProfileListView
)


urlpatterns = [
    path('investor-profile/<int:pk>/', InvestorProfileViewById.as_view(), 
         name='investor-profile-by-id'),
    path('investors/', InvestorProfileListView.as_view(),
         name='investors-list'),
    path('investor/<int:pk>/notifications-settings/',
         ProfileNotificationSettingsView.as_view(), 
         name='startup-notification-settings'
    ),
    path('investor/<int:pk>/notifications-settings/<int:notification_type>/',
         ProfileNotificationSettingsByIDView.as_view(), 
         name='startup-notification-settings-by-id'
    ),
    path('investor/<int:pk>/notifications/', ProfileNotificationsListView.as_view(),
         name='investor-notifications'),
]
