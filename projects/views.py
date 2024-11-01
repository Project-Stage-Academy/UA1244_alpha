import logging
from django.http import Http404
from django.core.exceptions import ValidationError
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
# from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Project
from startups.models import StartUpProfile
from .serializers import ( ProjectSerializerList,
                           UpdateProjectSerializer,
                           CreateProjectSerializer)

logger = logging.getLogger("django")

class ProjectsListView(generics.ListAPIView):
    """
    API view to get all startups projects
    """

    queryset = Project.objects.all()
    serializer_class = ProjectSerializerList
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        logger.info("Fetching list of projects")
        response = super().list(request, *args, **kwargs)
        logger.info(f"Fetched {len(response.data)} projects")
        return response

class StartupsProjectView(generics.ListAPIView):
    """
    API view for get list of sturtup's projects
    """
    serializer_class = ProjectSerializerList
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        logger.info(f"Fetched sturtup's project")
        startup = get_object_or_404(StartUpProfile, id=self.kwargs["startup_id"])

        project_list = Project.objects.filter(startup__id=startup.id)
        logger.info(f"Fetched projects for startup {startup.name}")
        return project_list
    

class CreateProjectsView(generics.CreateAPIView):
    """
    API view for create new project
    """
    serializer_class = CreateProjectSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        logger.info(f"Create project")
        startup = get_object_or_404(StartUpProfile, id=request.data["startup"])
        if startup.user_id.id != request.user.id:
            logger.error(f"User with id {request.user.id} don't have permission to create project", exc_info=True)
            return Response(
                {"error": "You do not have permission to create new project."},
                status=status.HTTP_403_FORBIDDEN,
            )
        try:
            response = super().create(request, *args, **kwargs)
            logger.info(f"Project was created successfully: {response.data["project_id"]}")
            return Response(
                {
                    "message": "New project created successfully",
                    "data": response.data,
                },
                status=status.HTTP_201_CREATED,
            )
        except ValidationError as e:
            logger.error(f"An error occurred while trying to create a new project {e.detail}", exc_info=True)
            return Response(
                {"error": "Invalid data", "details": e.detail},
                status=status.HTTP_400_BAD_REQUEST,
            )

class UpdateProjectView(generics.UpdateAPIView):
    serializer_class = UpdateProjectSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'

    def get_queryset(self):
        return Project.objects.filter(project_id=self.kwargs["pk"])
    
    def update(self, request, *args, **kwargs):
        logger.info("Update project")
        try:
            project = self.get_object()
        except Http404 as e:
            logger.error("Project not found", exc_info=True)
            return Response(
                {"error": "This project doesn't exist"},
                status=status.HTTP_404_NOT_FOUND,
            )
        
        if project.startup.user_id != request.user:
            logger.error(f"User with this id {request.user.id} don't has permission to update project.", exc_info=True)
            return Response(
                {"error": "You do not have permission to update this project."},
                status=status.HTTP_403_FORBIDDEN
            )
        try:
            response = super().update(request, *args, **kwargs)
            logger.info("Project was updated successfully")
            return Response(
                {
                    "message": "Project was updated successfully",
                    "data": response.data,
                },
                status=status.HTTP_200_OK,
                )
        except ValidationError as e:
            logger.error("Validation error occurred while updating project", exc_info=True)
            return Response(
                {"error": "Invalid data", "details": e.detail},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        