from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import InvestmentTracking
from startups.models import StartUpProfile
from django.db.utils import IntegrityError
from rest_framework.views import APIView
from investors.models import InvestorProfile
from .serializers import InvestmentTrackingSerializerCreate

class InvestmentTrackingSaveView(APIView):
    """
    API view to save StartUps that are of interest to Investors
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, sender_id):
        investor_profile = get_object_or_404(InvestorProfile, user=request.user)
        startup = get_object_or_404(StartUpProfile, id=sender_id)
        serializer = InvestmentTrackingSerializerCreate(data={'investor': investor_profile.id, 'startup': startup.id})
        if serializer.is_valid():
            try:
                investment_tracking = InvestmentTracking(investor=investor_profile, startup=startup)
                investment_tracking.save()
                return Response({"message": "StartUp has been successfully saved."}, status = status.HTTP_201_CREATED)
            except IntegrityError:
                return Response({"message": "Startup is already saved."}, status = status.HTTP_400_BAD_REQUEST)

        
            
