from django.urls import path
from .views import (
    TrackProjectFollowView,
    InvestorsProjectsListView)


urlpatterns = [
    path('investor-track-projects/', InvestorsProjectsListView.as_view(), name='project-list'),
    path('track/<uuid:project_id>/project', TrackProjectFollowView.as_view(), name="project-track"),
]
