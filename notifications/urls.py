from django.urls import path
from .views import NotificationsInvestorGet


urlpatterns = [
    path('investor/', NotificationsInvestorGet.as_view(), name = 'notifications-investor')
]
