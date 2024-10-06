from django.http import Http404
from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from profiles.models import StartUpProfile
from profiles.serializers import StartUpProfileSerializer


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
        return Response({
            'message': 'Startup profile created successfully',
            'data': response.data
        }, status=status.HTTP_201_CREATED)


class StartUpProfileUpdate(generics.UpdateAPIView):
    queryset = StartUpProfile.objects.all()
    serializer_class = StartUpProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return StartUpProfile.objects.filter(user_id=self.request.user)

    def update(self, request, *args, **kwargs):
        try:
            updating_obj = self.get_object()
        except Http404:
            return Response({
                'message': 'Startup profile not found'
            }, status=status.HTTP_404_NOT_FOUND)

        if updating_obj.user_id != request.user:
            raise PermissionDenied("You do not have permission to update this profile")

        response = super().update(request, *args, **kwargs)
        return Response({
            'message': 'Startup profile updated successfully',
            'data': response.data
        }, status=status.HTTP_200_OK)


class StartupProfileViewById(generics.RetrieveAPIView):
    queryset = StartUpProfile.objects.all()
    serializer_class = StartUpProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return StartUpProfile.objects.filter(pk=self.kwargs['pk'])

    def get_object(self):
        try:
            obj = StartUpProfile.objects.get(pk=self.kwargs['pk'])
        except Http404:
            raise Http404("Startup profile not found")
        return obj

    def retrieve(self, request, *args, **kwargs):
        try:
            obj = self.get_object()
        except Http404:
            return Response({
                'message': 'Startup profile not found'
            }, status=status.HTTP_404_NOT_FOUND)
        return Response(obj, status=status.HTTP_200_OK)
