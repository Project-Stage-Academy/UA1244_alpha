from django.urls import path
from .views import (
    ProjectsListView,
    CreateProjectsView,
    StartupsProjectView,
    UpdateProjectView
)

urlpatterns = [
    path('projects/', ProjectsListView.as_view(), name='project-list'),
    path('startup-project/<int:startup_id>/', StartupsProjectView.as_view(), name='startups-project'),
    path('create', CreateProjectsView.as_view(), name="project-create"),
    path('project/<uuid:pk>/update/', UpdateProjectView.as_view(), name="update-project")

]
