from rest_framework import serializersfrom profiles.models import StartUpProfileclass StartUpProfileSerializer(serializers.ModelSerializer):    class Meta:        model = StartUpProfile        fields = ['user_id', 'name', 'description', 'website', 'created_at', 'updated_at']