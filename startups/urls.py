from django.urls import path

from startups.views import (
    StartUpProfileCreate,
    StartUpProfilesView,
    StartUpProfileUpdate,
    StartUpProfileViewById,
)
from notifications.views import (
    ProfileNotificationSettingsView,
    ProfileNotificationSettingsByIDView,
    ProfileNotificationsListView
)


urlpatterns = [
    path('startups/', StartUpProfilesView.as_view(), name='startup-list'),
    path('create', StartUpProfileCreate.as_view(), name='startup-create'),
    path('startups/<int:pk>/', StartUpProfileUpdate.as_view(), name='startup-update'),
    path('startup-profile/<int:pk>/', StartUpProfileViewById.as_view(), name='startup-profile-by-id'),
    path('startup/<int:pk>/notifications-settings/',
         ProfileNotificationSettingsView.as_view(), 
         name='startup-notification-settings'
    ),
    path('startup/<int:pk>/notifications-settings/<int:notification_type>/',
         ProfileNotificationSettingsByIDView.as_view(), 
         name='startup-notification-settings-by-id'
    ),
    path('startup/<int:pk>/notifications/', ProfileNotificationsListView.as_view(),
         name='startup-notifications'),
]
