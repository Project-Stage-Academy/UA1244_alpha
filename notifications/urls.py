from django.urls import path

from .views import (
    NotificationListView,
    NotificiationByIDView,
    RolesNotificationsListCreateView,
    RoleNotificationsByIDView,
    NotificationPreferencesListView,
)


urlpatterns = [
    path('list/', NotificationListView.as_view(), name='notification_list'),
    path('notification/<int:pk>/', NotificiationByIDView.as_view(), name='notification_by_id'),
    path('roles_notifications', RolesNotificationsListCreateView.as_view(), name='roles_notifications'),
    path('roles_notifications/<int:pk>', RoleNotificationsByIDView.as_view(), name='role_notifications_by_id'),
    path('preferences/', NotificationPreferencesListView.as_view(), name='all-preferences')
]