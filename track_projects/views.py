import logging
from django.shortcuts import render
from django.http import Http404
from rest_framework import generics, status
from django.core.exceptions import ValidationError
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

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
        project = get_object_or_404(Project, project_id=self.kwargs["project_id"])
        investor_profile = get_object_or_404(InvestorProfile, user=request.user)

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
            logger.error(f"Validation error while investor {request.user.id} tried to follow project {project.project_id}. Error: {e.detail}")
            return Response(
                {'error': 'Invalid data', 
                 'more information': e.detail},
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
