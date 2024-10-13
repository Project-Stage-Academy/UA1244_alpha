from rest_framework import serializers

from startups.models import StartUpProfile


class StartUpProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = StartUpProfile
        fields = ['name', 'description', 'startup_logo', 'website']
