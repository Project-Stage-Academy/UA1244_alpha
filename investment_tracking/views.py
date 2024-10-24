import logging
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

logger = logging.getLogger('django')


class InvestmentTrackingSaveView(APIView):
    """
    API view to save StartUps that are of interest to Investors
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, startup_id):
        logger.debug(f"Received POST request to save Startup with ID: {startup_id} for user: {request.user}")

        investor_profile = get_object_or_404(InvestorProfile, user=request.user)
        logger.debug(f"Investor profile found: {investor_profile}")

        startup = get_object_or_404(StartUpProfile, id=startup_id)
        logger.debug(f"Startup profile found: {startup}")

        serializer = InvestmentTrackingSerializerCreate(data={'investor': investor_profile.id, 'startup': startup.id})

        if serializer.is_valid():
            try:
                investment_tracking = InvestmentTracking(investor=investor_profile, startup=startup)
                investment_tracking.save()
                logger.debug(f"InvestmentTracking object created: {investment_tracking}")
                return Response({"message": "StartUp has been successfully saved."}, status=status.HTTP_201_CREATED)
            except IntegrityError:
                logger.warning(
                    f"Attempt to save Startup that is already saved for Investor: {investor_profile}, Startup: {startup}")
                return Response({"message": "Startup is already saved."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            logger.error(f"Serializer validation failed: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
