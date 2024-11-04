from django.urls import path
from .views import InvestorsNotificationsListView

from .views import NotificationListView, NotificiationByIDView


urlpatterns = [
    path('investor/', InvestorsNotificationsListView.as_view(), name = 'notifications-investor')
    path('list/', NotificationListView.as_view(), name='notification_list'),
    path('notification/<int:pk>/', NotificiationByIDView.as_view(), name='notification_by_id'),
]

