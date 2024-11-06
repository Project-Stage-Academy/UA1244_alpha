import logging
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, generics
from .models import InvestmentTracking
from startups.models import StartUpProfile
from django.db.utils import IntegrityError
from rest_framework.views import APIView
from investors.models import InvestorProfile
from .serializers import InvestmentTrackingSerializerCreate, ListInvestmentTrackingSerializer

def get_investor_profile(request):
    return get_object_or_404(InvestorProfile, user=request.user)


logger = logging.getLogger('django')


class InvestmentTrackingSaveView(APIView):
    """
    API view to save StartUps that are of interest to Investors
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, startup_id):
        logger.debug(f"Received POST request to save Startup with ID: {startup_id} for user: {request.user}")

        investor_profile = get_investor_profile(request)
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
                return Response({"message": "Startup is already saved."}, status=status.HTTP_409_CONFLICT)
        else:
            logger.error(f"Serializer validation failed: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InvestmentTrackingListView(generics.ListAPIView):
    """
    API view to get list all startups saved by the investor.
    """
    permission_classes = [IsAuthenticated]
    queryset = None
    serializer_class = ListInvestmentTrackingSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['startup__name']
    ordering_fields = ['saved_at', 'startup__name']

    def get_queryset(self):
        investor_profile = get_investor_profile(self.request)
        logger.debug(f"Investor profile found: {investor_profile}")
        return InvestmentTracking.objects.filter(investor=investor_profile)


class InvestmentTrackingUnsaveView(APIView):
    """
    API view to unfollow a saved startup.
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request, startup_id):
        logger.debug(f"Request to unsave Startup with ID: {startup_id}, user: {request.user}")

        investor_profile = get_investor_profile(request)
        logger.debug(f"Investor profile found: {investor_profile}")

        startup = get_object_or_404(StartUpProfile, id=startup_id)
        logger.debug(f"Startup profile found: {startup}")

        investment_tracking = get_object_or_404(InvestmentTracking, investor=investor_profile, startup=startup)
        investment_tracking.delete()
        logger.debug(f"Successfully unsaved Startup: {startup} for Investor: {investor_profile}")
        return Response({"message": "StartUp has been successfully unsaved."}, status=status.HTTP_204_NO_CONTENT)
