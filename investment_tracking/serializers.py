from rest_framework import serializers
from .models import InvestmentTracking


class InvestmentTrackingSerializerCreate(serializers.ModelSerializer):

    class Meta:
        model = InvestmentTracking
        fields = ['investor', 'startup']


class ListInvestmentTrackingSerializer(serializers.ModelSerializer):
    startup_name = serializers.CharField(source='startup.name', read_only=True)

    class Meta:
        model = InvestmentTracking
        fields = ['startup', 'startup_name', 'saved_at']
