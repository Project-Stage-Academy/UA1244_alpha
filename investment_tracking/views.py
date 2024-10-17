from django.shortcuts import get_object_or_404

from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .serializers import InvestmentTrackingSerializer
from .models import InvestmentTracking
from startups.models import StartUpProfile
from django.http import Http404
from django.db.utils import IntegrityError
from rest_framework.views import APIView
from investors.models import InvestorProfile

class InvestmentTrackingSaveView(APIView):
    serializer_class = InvestmentTrackingSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, startup_id):
        investor = request.user
        investor_profile = get_object_or_404(InvestorProfile, user=investor)
        startup = get_object_or_404(StartUpProfile, id=startup_id)

        try:
            investment_tracking = InvestmentTracking(investor=investor_profile, startup=startup)
            investment_tracking.save()
            return Response({"message": "StartUp has been successfully saved."}, status = status.HTTP_201_CREATED)
        except IntegrityError:
            return Response({"error": "Startup is already saved."}, status = status.HTTP_400_BAD_REQUEST)
            
