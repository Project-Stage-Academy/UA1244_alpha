import logging
from django.shortcuts import render
from django.http import Http404
from rest_framework import generics, status
from django.core.exceptions import ValidationError
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
import uuid

from .models import TrackProjects
from projects.models import Project
from investors.models import InvestorProfile
from .serializers import TrackProjectSerializerCreate, TrackProjectSerializerGet

logger = logging.getLogger("django")

class TrackProjectFollowView(generics.CreateAPIView):
    """
    API view for investors to follow a project.
   
    Methods:
        - POST: Creates a new 'TrackProject' record associating the authenticated investor 
                with the project specified by 'project_id'.
    
    Raises:
        - Http404: If the project or investor profile is not found.
        - ValidationError: If invalid data is provided during the creation process.
    
    Returns:
        - 201 Created: When the subscription is successful.
        - 400 Bad Request: If the provided data is invalid.
    """

    serializer_class = TrackProjectSerializerCreate
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        logger.info(f"Investor {request.user.id} is attempting to follow a project.")

        project = Project.objects.filter(project_id=self.kwargs["project_id"]).first()
        investor_profile = InvestorProfile.objects.filter(user=request.user).first()
        if not project:
            logger.error(f"Project not found")
            return Response(
                {'error': 'Project not found'},
                status = status.HTTP_404_NOT_FOUND
            )
        
        if not investor_profile:
            logger.error(f"Investor not found")
            return Response(
                {'error': 'Investor not found'},
                status = status.HTTP_404_NOT_FOUND
            )

        if TrackProjects.objects.filter(investor=investor_profile, project=project).exists():
            logger.error(f"Investor {request.user.id} is already tracking project {project.project_id}.")
            return Response(
                {"error": "You are already tracking this project."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        data = {
            'project': project.project_id,  
            'investor': investor_profile.id 
        }

        data.update(request.data)

        serializer = self.get_serializer(data=data)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            logger.info(f"Investor {investor_profile.id} successfully followed project {project.project_id}.")
            return Response(
                {'message': f'You successfully subscribed to project {project.title}'},
                status=status.HTTP_201_CREATED
            )
        except ValidationError as e:
            logger.error(f"ValidationError: {e.detail}")
            return Response(
                {'error': 'Invalid data', 
                 'details': e.detail},
                 status=status.HTTP_400_BAD_REQUEST
            )


class InvestorsProjectsListView(generics.ListAPIView):
    """
    API view for listing the projects followed by an investor.
        
    Methods:
        - GET: Returns a list of projects that the authenticated investor is following.
    
    Returns:
        - 200 OK: With a list of projects being tracked by the investor.
    """

    serializer_class = TrackProjectSerializerGet
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        logger.info(f"Fetching tracked projects for investor {self.request.user.id}.")
        tracked_list = TrackProjects.objects.filter(investor__user__id=self.request.user.id)
        logger.info(f"Investor {self.request.user.id} is following {tracked_list.count()} projects.")
        return tracked_list
