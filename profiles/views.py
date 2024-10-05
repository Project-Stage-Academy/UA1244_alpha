from django.shortcuts import render
from rest_framework import generics
from models import StartUpProfile
from profiles.serializers import StartUpProfileSerializer


class StartUpProfilesView(generics.ListAPIView):  #show all objects from base
    queryset = StartUpProfile.objects.all()
    serializer_class = StartUpProfileSerializer
