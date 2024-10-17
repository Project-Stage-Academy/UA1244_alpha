from rest_framework import serializers
from .models import InvestmentTracking

class InvestmentTrackingSerializer(serializers.ModelSerializer):

    class Meta:
        model = InvestmentTracking
        fields = ['investor', 'startup']