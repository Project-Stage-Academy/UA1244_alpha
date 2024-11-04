import logging
from django.http import Http404
from django.core.exceptions import ValidationError
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
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
        try:
            response = super().list(request, *args, **kwargs)
            logger.info(f"Fetched {len(response.data)} projects successfully")
            return response
        except Exception as e:
            logger.error(f"Error fetching project list: {str(e)}", exc_info=True)
            return Response(
                {"error": "An error occurred while fetching projects."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


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
        logger.info(f"Fetching projects for startup {self.kwargs['startup_id']}")
        startup = get_object_or_404(StartUpProfile, id=self.kwargs["startup_id"])

        project_list = Project.objects.filter(startup__id=startup.id)
        logger.info(f"Fetched {len(project_list)} projects for startup {startup.name}")
        return project_list

    def list(self, request, *args, **kwargs):
        try:
            return super().list(request, *args, **kwargs)
        except Http404 as e:
            logger.error("Startup not found", exc_info=True)
            return Response(
                {"error": "Startup not found."},
                status=status.HTTP_404_NOT_FOUND,
            )


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
        logger.info(f"User {request.user.id} attempting to create a project")
        startup = get_object_or_404(StartUpProfile, id=request.data["startup"])
        if startup.user_id.id != request.user.id:
            logger.warning(f"User {request.user.id} does not have permission to create a project for startup {startup.id}")
            return Response(
                {"error": "You do not have permission to create a new project."},
                status=status.HTTP_403_FORBIDDEN,
            )
        try:
            response = super().create(request, *args, **kwargs)
            logger.info(f"Project created successfully for startup {startup.id}")
            return Response(
                {
                    "message": "New project created successfully",
                    "data": response.data,
                },
                status=status.HTTP_201_CREATED,
            )
        except ValidationError as e:
            logger.error(f"Validation error while creating project: {e.detail}", exc_info=True)
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
        logger.info(f"Fetching project {self.kwargs['pk']} for update")
        return Project.objects.filter(project_id=self.kwargs["pk"])

    def update(self, request, *args, **kwargs):
        logger.info(f"User {request.user.id} attempting to update project {self.kwargs['pk']}")
        try:
            project = self.get_object()
        except Http404:
            logger.error(f"Project {self.kwargs['pk']} not found", exc_info=True)
            return Response(
                {"error": "This project doesn't exist"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if project.startup.user_id != request.user:
            logger.warning(f"User {request.user.id} does not have permission to update project {self.kwargs['pk']}")
            return Response(
                {"error": "You do not have permission to update this project."},
                status=status.HTTP_403_FORBIDDEN,
            )
        try:
            response = super().update(request, *args, **kwargs)
            logger.info(f"Project {self.kwargs['pk']} updated successfully")
            return Response(
                {
                    "message": "Project was updated successfully",
                    "data": response.data,
                },
                status=status.HTTP_200_OK,
            )
        except ValidationError as e:
            logger.error(f"Validation error while updating project {self.kwargs['pk']}: {e.detail}", exc_info=True)
            return Response(
                {"error": "Invalid data", "details": e.detail},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ProjectViewById(generics.RetrieveAPIView):
    """
    API view to retrieve a project by its ID.

    Methods:
        - GET: Retrieves the project details by ID.

    Returns:
        - 200 OK: If the project is retrieved successfully.
        - 404 Not Found: If the project is not found.
    """
    serializer_class = ProjectSerializerList
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        logger.info(f"Fetching project by ID {self.kwargs['pk']}")
        return Project.objects.filter(project_id=self.kwargs.get('pk'))

    def retrieve(self, request, *args, **kwargs):
        logger.info(f"User {request.user.id} attempting to retrieve project {self.kwargs['pk']}")
        try:
            obj = self.get_object()
            logger.info(f"Project {obj.project_id} retrieved successfully")
            return Response(self.get_serializer(obj).data)
        except Http404:
            logger.error(f"Project {self.kwargs['pk']} not found", exc_info=True)
            return Response(
                {"error": "This project doesn't exist"},
                status=status.HTTP_404_NOT_FOUND,
            )
