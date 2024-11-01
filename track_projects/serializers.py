import logging
from rest_framework import serializers
from .models import TrackProjects

logger = logging.getLogger('django')

class TrackProjectSerializerCreate(serializers.ModelSerializer):
    """
    Serializer for creating TrackProjects instances.
    """

    class Meta:
        model = TrackProjects
        fields = ['investor', 'project']


class TrackProjectSerializerGet(serializers.ModelSerializer):
    """
    Serializer for retrieving TrackProjects instances with additional project details.
    
    This serializer is used to fetch details of TrackProjects records, including the associated 
    project's title (as 'project_name')
    """
    project_name = serializers.CharField(source='project.title', read_only=True)

    class Meta:
        model = TrackProjects
        fields = ['id', 'investor', 'project', 'project_name', 'saved_at']
