import logging
from rest_framework import serializers
from .models import InvestmentTracking


logger = logging.getLogger('django')


class InvestmentTrackingSerializerCreate(serializers.ModelSerializer):

    class Meta:
        model = InvestmentTracking
        fields = ['investor', 'startup']

    def create(self, validated_data):
        logger.info(f"Creating InvestmentTracking with data: {validated_data}")
        investment_tracking = super().create(validated_data)
        logger.info(f"InvestmentTracking created successfully: {investment_tracking}")
        return investment_tracking


class ListInvestmentTrackingSerializer(serializers.ModelSerializer):
    startup_name = serializers.CharField(source='startup.name', read_only=True)

    class Meta:
        model = InvestmentTracking
        fields = ['startup', 'startup_name', 'saved_at']
