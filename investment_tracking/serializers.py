from rest_framework import serializers
from .models import InvestmentTracking



class InvestmentTrackingSerializerCreate(serializers.ModelSerializer):

    class Meta:
        model = InvestmentTracking
        fields = ['investor', 'startup']


class InvestmentTrackingSerializerGet(serializers.ModelSerializer):

    class Meta:
        model = InvestmentTracking
        fields = '__all__'