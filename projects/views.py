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
from .serializers import (ProjectSerializerList,
                          UpdateProjectSerializer,
                          CreateProjectSerializer)

logger = logging.getLogger("django")

class ProjectsListView(generics.ListAPIView):
    """
    API view to get all startups' projects.

    Methods:
        - GET: Retrieves all projects.
    
    Returns:
        - 200 OK: A list of projects.
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
    API view to get a list of a startup's projects.

    Methods:
        - GET: Retrieves projects filtered by startup.

    Returns:
        - 200 OK: A list of the startup's projects.
        - 404 Not Found: If the startup is not found.
    """

    serializer_class = ProjectSerializerList
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        logger.info(f"Fetching startup's projects")
        startup = get_object_or_404(StartUpProfile, id=self.kwargs["startup_id"])

        project_list = Project.objects.filter(startup__id=startup.id)
        logger.info(f"Fetched projects for startup {startup.name}")
        return project_list


class CreateProjectsView(generics.CreateAPIView):
    """
    API view to create a new project.

    Methods:
        - POST: Creates a new project.

    Returns:
        - 201 Created: If the project is created successfully.
        - 400 Bad Request: If the provided data is invalid.
        - 403 Forbidden: If the user does not have permission to create a project for the startup.
    """

    serializer_class = CreateProjectSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        logger.info(f"Creating project")
        startup = get_object_or_404(StartUpProfile, id=request.data["startup"])
        if startup.user_id.id != request.user.id:
            logger.error(f"User with id {request.user.id} doesn't have permission to create project", exc_info=True)
            return Response(
                {"error": "You do not have permission to create a new project."},
                status=status.HTTP_403_FORBIDDEN,
            )
        try:
            response = super().create(request, *args, **kwargs)
            logger.info(f"Project was created successfully")
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
    """
    API view to update an existing project.

    Methods:
        - PUT/PATCH: Updates the project details.

    Returns:
        - 200 OK: If the project is updated successfully.
        - 400 Bad Request: If the provided data is invalid.
        - 403 Forbidden: If the user does not have permission to update the project.
        - 404 Not Found: If the project is not found.
    """

    serializer_class = UpdateProjectSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'

    def get_queryset(self):
        return Project.objects.filter(project_id=self.kwargs["pk"])
    
    def update(self, request, *args, **kwargs):

        logger.info("Updating project")
        try:
            project = self.get_object()
        except Http404 as e:
            logger.error("Project not found", exc_info=True)
            return Response(
                {"error": "This project doesn't exist"},
                status=status.HTTP_404_NOT_FOUND,
            )
        
        if project.startup.user_id != request.user:
            logger.error(f"User with id {request.user.id} doesn't have permission to update the project.", exc_info=True)
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

class ProjectViewById(generics.RetrieveAPIView):
    serializer_class = ProjectSerializerList
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Project.objects.filter(project_id=self.kwargs.get('pk'))

    def retrieve(self, request, *args, **kwargs): 
        try:
            obj = self.get_object()
            logger.info(f"Project retrieved successfully: {obj.project_id}")
            return Response(self.get_serializer(obj).data)  
        except Http404:
            return Response(
                {"error": "This project doesn't exist"},
                status=status.HTTP_404_NOT_FOUND,
            )
