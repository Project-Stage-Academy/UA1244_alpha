from rest_framework import serializers
from .models import Project

class ProjectSerializerList(serializers.ModelSerializer):

    """Serializer for get list of Projects"""

    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = '__all__'


class CreateProjectSerializer(serializers.ModelSerializer):

    """Serializer for creaet new Project"""

    class Meta:
        model = Project
        fields = ['title', 'startup', 'risk', 'description', 'business_plan', 
                  'amount', 'status', 'duration']


class UpdateProjectSerializer(serializers.ModelSerializer):
    """Serializer for update new Project"""

    class Meta:
        model = Project
        fields = ['title', 'risk', 'description', 'business_plan', 
                  'amount', 'status', 'duration']
    

