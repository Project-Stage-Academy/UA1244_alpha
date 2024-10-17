from django.shortcuts import render, get_object_or_404

from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, status
from .serializers import InvestmentTrackingSerializer
from .models import InvestmentTracking
from startups.models import StartUpProfile
from django.http import Http404
from django.db.utils import IntegrityError
from rest_framework.views import APIView

class InvestmentTrackingSaveView(APIView):
    serializer_class = InvestmentTrackingSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, startup_id):
        investor = request.user
        startup = get_object_or_404(StartUpProfile, id=startup_id)

        # try:
        #     startup = get_object_or_404(StartUpProfile, id=startup_id)
        # except Http404:
        #     return Response({"error": "Unfortunately, cannot find this StartUp"}, status=status.HTTP_404_NOT_FOUND)

        try:
            investment_tracking = InvestmentTracking(investor=investor, startup=startup)
            investment_tracking.save()
            return Response({"message": "StartUp has been successfully saved."}, status = status.HTTP_201_CREATED)
        except IntegrityError:
            return Response({"error": "Startup is already saved."}, status = status.HTTP_400_BAD_REQUEST)
            
