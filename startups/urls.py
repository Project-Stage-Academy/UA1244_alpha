from django.urls import path

from startups.views import (
    StartUpProfileCreate,
    StartUpProfilesView,
    StartUpProfileUpdate,
    StartUpProfileViewById,
)


urlpatterns = [
    path('startups/', StartUpProfilesView.as_view(), name='startup-list'),
    path('create', StartUpProfileCreate.as_view(), name='startup-create'),
    path('startups/<int:pk>/', StartUpProfileUpdate.as_view(), name='startup-update'),
    path('startup-profile/<int:pk>/', StartUpProfileViewById.as_view(), name='startup-profile-by-id'),
]
