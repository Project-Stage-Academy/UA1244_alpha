from django.urls import path
from .views import InvestorsNotificationsListView


urlpatterns = [
    path('investor/', InvestorsNotificationsListView.as_view(), name = 'notifications-investor')
]
