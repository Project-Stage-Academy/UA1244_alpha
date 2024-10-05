from django.shortcuts import render
from rest_framework import generics
from profiles.models import StartUpProfile
from profiles.serializers import StartUpProfileSerializer


class StartUpProfilesView(generics.ListAPIView):  #pagination???
    queryset = StartUpProfile.objects.all()

    serializer_class = StartUpProfileSerializer


class StartUpProfileCreate(generics.CreateAPIView):
    serializer_class = StartUpProfileSerializer


class StartUpProfileUpdate(generics.UpdateAPIView):
    queryset = StartUpProfile.objects.all()
    serializer_class = StartUpProfileSerializer

class StartupProfileViewById(generics.RetrieveAPIView):
    queryset = StartUpProfile.objects.all()
    serializer_class = StartUpProfileSerializer

