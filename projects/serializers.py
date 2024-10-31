from rest_framework import serializers
from .models import Project
from datetime import timedelta

class ProjectSerializerList(serializers.ModelSerializer):

    """Serializer for get list of Projects"""

    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = '__all__'



class BaseProjectSerializer(serializers.ModelSerializer):
    """ Base Project Serializer to emulate the validation functions 
        for creating and updating projects
    """

    def validate_duration(self, value):
        if value < timedelta(0):
            raise serializers.ValidationError("Duration cannot be negative.")
        return value


class CreateProjectSerializer(BaseProjectSerializer):

    """Serializer for creaet new Project"""

    class Meta:
        model = Project
        fields = ['title', 'startup', 'risk', 'description', 'business_plan', 
                  'amount', 'status', 'duration']


class UpdateProjectSerializer(BaseProjectSerializer):
    """Serializer for update new Project"""

    class Meta:
        model = Project
        fields = ['title', 'risk', 'description', 'business_plan', 
                  'amount', 'status', 'duration']
    

