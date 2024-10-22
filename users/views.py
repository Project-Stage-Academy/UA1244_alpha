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
from datetime import datetime

# import datetime
from rest_framework_simplejwt.exceptions import TokenError
from django.core.cache import cache


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

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.set_exp(lifetime=timedelta(seconds=0))
                expiration_time = datetime.fromtimestamp(token["exp"])
                print(expiration_time)
            else:
                return Response({"error": "The refresh token hadn't been provided"}, status=status.HTTP_400_BAD_REQUEST)
            access_token = request.auth.token
            try:
                ac = AccessToken(access_token)

                ac.set_exp(lifetime=timedelta(seconds=0))
                # ac.delete()
                # cache_key = f"user_{request.user.id}_token"
                # cache.delete(cache_key)
                # expiration_time = datetime.fromtimestamp(ac["exp"])
                # print(expiration_time)
                # return Response({"message": "The user logout successful"}, status=status.HTTP_200_OK)
                response = Response({"message": "User logged out successfully"}, status=status.HTTP_200_OK)
                # response.delete_cookie('access')
                # response.delete_cookie('refresh')
                response.delete_cookie('access_token')
                response.delete_cookie('refresh_token')
                return response
            except TokenError:
                return Response({"error": "Invalid access token"}, status=status.HTTP_400_BAD_REQUEST)  
        except Exception as e:
            return Response({"error":f"{e}"}, status=status.HTTP_400_BAD_REQUEST)
