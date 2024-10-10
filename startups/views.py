from django.http import Http404
from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from startups.models import StartUpProfile
from startups.serializers import StartUpProfileSerializer
from startups.utils import (
    get_success_response,
    handle_object_not_found
)


class StartUpProfilesView(generics.ListAPIView):
    queryset = StartUpProfile.objects.all()
    pagination_class = PageNumberPagination
    serializer_class = StartUpProfileSerializer
    permission_classes = [IsAuthenticated]

    ordering_fields = ['name', 'created_at']
    ordering = ['created_at']


class StartUpProfileCreate(generics.CreateAPIView):
    serializer_class = StartUpProfileSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return get_success_response('Startup profile created successfully', response.data, status.HTTP_201_CREATED)


class StartUpProfileUpdate(generics.UpdateAPIView):
    queryset = StartUpProfile.objects.all()
    serializer_class = StartUpProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return StartUpProfile.objects.filter(user_id=self.request.user)

    def update(self, request, *args, **kwargs):
        try:
            updating_obj = self.get_object()
        except Http404 as e:
            return handle_object_not_found(e)

        if updating_obj.user_id != request.user:
            raise PermissionDenied("You do not have permission to update this profile")

        response = super().update(request, *args, **kwargs)
        return get_success_response('Startup profile updated successfully', response.data)


class StartupProfileViewById(generics.RetrieveAPIView):
    queryset = StartUpProfile.objects.all()
    serializer_class = StartUpProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return StartUpProfile.objects.filter(pk=self.kwargs['pk'])

    def retrieve(self, request, *args, **kwargs):
        try:
            obj = self.get_object()
        except Http404 as e:
            return handle_object_not_found(e)

        return Response(obj, status=status.HTTP_200_OK)
