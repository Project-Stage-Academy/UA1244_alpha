from rest_framework import serializers

from .models import InvestorProfile


class InvestorSerializer(serializers.ModelSerializer):
    """Investor Serializer"""
    
    class Meta:
        model = InvestorProfile
        fields = '__all__'