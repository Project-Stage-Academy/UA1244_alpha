from django.contrib import admin
from django.urls import path

from profiles.views import StartUpProfilesView


urlpatterns = [
    path('startups/', StartUpProfilesView.as_view(), name='startup-list'),
]
