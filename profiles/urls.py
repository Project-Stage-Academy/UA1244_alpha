from django.contrib import admin
from django.urls import path

from profiles.views import StartUpProfilesView, StartUpProfileCreate, StartUpProfileUpdate, StartupProfileViewById

urlpatterns = [
    path('startups/', StartUpProfilesView.as_view(), name='startup-list'),
    path('create', StartUpProfileCreate.as_view(), name='startup-create'),
    path('startups/<int:pk>/', StartUpProfileUpdate.as_view(), name='startup-update'),
    path('startup-profile/<int:pk>/', StartupProfileViewById.as_view(), name='profile-by-id')
]
