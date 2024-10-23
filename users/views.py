from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from rest_framework import status
from .models import User
from .serializers import UserSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from datetime import timedelta


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


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    """
    View for successfull user log out
    """

    def post(self, request):
        refresh_token = request.data["refresh"]
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.set_exp(lifetime=timedelta(seconds=0))
        else:
            return Response({"error": "The refresh token hadn't been provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        access_token = request.auth.token
        ac_token = AccessToken(access_token)
        ac_token.set_exp(lifetime=timedelta(seconds=0))
        return Response({"message": "User logged out successfully"}, status=status.HTTP_200_OK)
