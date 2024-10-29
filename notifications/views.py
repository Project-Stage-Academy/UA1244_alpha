from django.shortcuts import render
from rest_framework import generics, status
from .serializers import NotificationForInvestorSerializersList
from rest_framework.permissions import IsAuthenticated
from .models import Notification
from investors.models import InvestorProfile
from django.shortcuts import get_object_or_404


class InvestorsNotificationsListView(generics.ListAPIView):
    """API view for get investors notifications"""

    serializer_class = NotificationForInvestorSerializersList
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        investor = get_object_or_404(InvestorProfile, user=self.request.user)
        return Notification.objects.filter(investor=investor.id).order_by('-created_at')

