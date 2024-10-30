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
        # logger.info("Fetching list of projects")
        response = super().list(request, *args, **kwargs)
        return response

class SturtupsProjectView(generics.ListAPIView):
    """
    API view for get list of sturtup's projects
    """
    serializer_class = ProjectSerializerList
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        startup = get_object_or_404(StartUpProfile, id=self.kwargs["startup_id"])

        project_list = Project.objects.filter(startup__id=startup.id)
        return project_list
    

class CreateProjectsView(generics.CreateAPIView):
    """
    API view for create new project
    """
    serializer_class = CreateProjectSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        startup = get_object_or_404(StartUpProfile, id=request.data["startup"])
        if startup.user_id.id != request.user.id:
            return Response(
                {"error": "You do not have permission to create new project."},
                status=status.HTTP_403_FORBIDDEN,
            )
        try:
            response = super().create(request, *args, **kwargs)
            return Response(
                {
                    "message": "New project created successfully",
                    "data": response.data,
                },
                status=status.HTTP_201_CREATED,
            )
        except ValidationError as e:
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
        try:
            project = self.get_object()
        except Http404 as e:
            return Response(
                {"error": "This project doesn't exist"},
                status=status.HTTP_404_NOT_FOUND,
            )
        
        if project.startup.user_id != request.user:
            return Response(
                {"error": "You do not have permission to update this project."},
                status=status.HTTP_403_FORBIDDEN
            )
        try:
            response = super().update(request, *args, **kwargs)
            return Response(
                {
                    "message": "Project was updated successfully",
                    "data": response.data,
                },
                status=status.HTTP_200_OK,
                )
        except ValidationError as e:
            return Response(
                {"error": "Invalid data", "details": e.detail},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        