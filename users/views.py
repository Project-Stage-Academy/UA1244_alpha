from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from rest_framework import status
from .models import User
from .serializers import UserSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Obtains a token pair for a user.

    :param request: The incoming request.
    :param args: Additional arguments.
    :param kwargs: Additional keyword arguments.
    :return: A response containing the token pair.
    """
    serializer_class = TokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        """
        Handles the POST request.

        :param request: The incoming request.
        :param args: Additional arguments.
        :param kwargs: Additional keyword arguments.
        :return: A response containing the token pair.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        tokens = serializer.validated_data
        user = User.objects.get(email=request.data['email'])

        return Response({
            'refresh': str(tokens['refresh']),
            'access': str(tokens['access']),
            'user_id': user.id,
            'email': user.email,
        }, status=status.HTTP_200_OK)


class UserProfileView(APIView):
    """
    Retrieves the user's profile information.

    :param request: The incoming request.
    :return: A response containing the user's profile information.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Handles the GET request.

        :param request: The incoming request.
        :return: A response containing the user's profile information.
        """
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)

