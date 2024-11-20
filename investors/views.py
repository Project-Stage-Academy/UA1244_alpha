from rest_framework import generics
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import InvestorProfile
from .serializers import InvestorSerializer


class InvestorProfileViewById(generics.RetrieveUpdateDestroyAPIView):
    """API view to GET, UPDADE, DELETE investor by id"""
    queryset = InvestorProfile.objects.all()
    serializer_class = InvestorSerializer
    permission_classes = [IsAuthenticated]


class InvestorProfileListView(generics.ListCreateAPIView):
    """API view to GET, UPDADE, DELETE investor by id"""
    queryset = InvestorProfile.objects.all()
    serializer_class = InvestorSerializer
    permission_classes = [IsAuthenticated]
