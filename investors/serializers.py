from rest_framework import serializers

from django.contrib.auth import get_user_model

from .models import InvestorProfile


User = get_user_model()

class InvestorSerializer(serializers.ModelSerializer):
    """Investor Serializer"""    
    class Meta:
        model = InvestorProfile
        fields = '__all__'

    def create(self, validated_data):
        user = validated_data.pop('user')
        validated_data['user'] = User.objects.get(id=user.id)
        investor_profile = InvestorProfile.objects.create(**validated_data)
        return investor_profile
