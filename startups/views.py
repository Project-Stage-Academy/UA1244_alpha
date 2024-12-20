import logging
from django.http import Http404
from django.core.exceptions import ValidationError
from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from startups.filters import StartUpProfileFilter
from startups.models import StartUpProfile
from startups.serializers import StartUpProfileSerializer
from startups.utils import (
    get_success_response,
    handle_object_not_found
)


logger = logging.getLogger('django')


class StartUpProfilesView(generics.ListAPIView):
    """
    API view to list all startup profiles with filtering and pagination.
    """
    queryset = StartUpProfile.objects.all()
    serializer_class = StartUpProfileSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = StartUpProfileFilter

    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['created_at']

    def list(self, request, *args, **kwargs):
        logger.info("Fetching startup profiles")
        response = super().list(request, *args, **kwargs)
        logger.info(f"Fetched {len(response.data)} startup profiles")
        return response


class StartUpProfileCreate(generics.CreateAPIView):
    """
    API view to create a new startup profile.
    """
    serializer_class = StartUpProfileSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        logger.info("Creating a new startup profile")
        try:
            response = super().create(request, *args, **kwargs)
            logger.info(f"Startup profile created successfully: {response.data['id']}")
            return Response(
                {
                    "message": "Startup profile created successfully",
                    "data": response.data
                },
                status=status.HTTP_201_CREATED
            )
        except ValidationError as e:
            logger.error("Validation error occurred while creating startup profile", exc_info=True)
            return Response(
                {"error": "Invalid data", "details": e.detail},
                status=status.HTTP_400_BAD_REQUEST
            )
        except PermissionDenied as e:
            logger.error("Permission denied error while creating startup profile", exc_info=True)
            return Response(
                {"error": "Permission denied", "details": str(e)},
                status=status.HTTP_403_FORBIDDEN
            )


class StartUpProfileUpdate(generics.UpdateAPIView):
    """
    API view to update an existing startup profile.
    """
    queryset = StartUpProfile.objects.all()
    serializer_class = StartUpProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return StartUpProfile.objects.filter(user_id=self.request.user.id)

    def update(self, request, *args, **kwargs):
        logger.info("Updating startup profile")
        try:
            updating_obj = self.get_object()
        except Http404 as e:
            logger.error("Startup profile not found", exc_info=True)
            return handle_object_not_found(e)

        if updating_obj.user_id != request.user:
            logger.error("User does not have permission to update this profile")
            raise PermissionDenied("You do not have permission to update this profile.")

        response = super().update(request, *args, **kwargs)
        logger.info(f"Startup profile updated successfully: {response.data['id']}")
        return get_success_response(
            message='Startup profile updated successfully',
            data=response.data
        )


class StartUpProfileViewById(generics.RetrieveAPIView):
    """
    API view to retrieve a specific startup profile by ID.
    """
    queryset = StartUpProfile.objects.all()
    serializer_class = StartUpProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return StartUpProfile.objects.filter(id=self.kwargs.get('pk'))

    def retrieve(self, request, *args, **kwargs):
        logger.info(f"Retrieving startup profile with ID: {self.kwargs['pk']}")
        try:
            obj = self.get_object()
            logger.info(f"Startup profile retrieved successfully: {obj.id}")
        except Http404 as e:
            return handle_object_not_found(e)

        return Response(obj, status=status.HTTP_200_OK)
