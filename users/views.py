import logging
from djoser.views import UserViewSet
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import UserRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from rest_framework import status
from .models import User
from .serializers import UserSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from datetime import timedelta




from .logic import *

logger = logging.getLogger('users')


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
        logger.debug(f"Token obtain attempt for user with email: {request.data.get('email')}")

        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            tokens = serializer.validated_data
            user = User.objects.get(email=request.data['email'])

            logger.info(
                "Successfully generated token pair",
                extra={
                    'user_id': user.id,
                    'email': user.email,
                }
            )
            
            # print(f'{user.id}: {tokens['refresh']}')
            logger.info("Successfully generated token print",
                extra={
                    'user_id': user.id,
                    'token': tokens['refresh'],
                })

            test = store_refresh_token(user.id, str(tokens['refresh']), 60)
            if not test:
                test = "fff"
            response = Response({
                'refresh': str(tokens['refresh']),
                'access': str(tokens['access']),
                'test': str(test),
                'user_id': user.id,
                'email': user.email,
                
            }, status=status.HTTP_200_OK)

            print(f'{user.id}: {response['refresh']}')

            

            return response
            
            # return Response({
            #     'refresh': str(tokens['refresh']),
            #     'access': str(tokens['access']),
            #     'user_id': user.id,
            #     'email': user.email,
            # }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(
                "Failed to generate token pair",
                extra={
                    'email': request.data.get('email'),
                    'error': str(e)
                }
            )
            raise


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
        logger.debug(f"Profile request for user: {user.email}")

        try:
            serializer = UserSerializer(user)
            logger.info(
                "Successfully retrieved user profile",
                extra={
                    'user_id': user.id,
                    'email': user.email
                }
            )
            return Response(serializer.data)

        except Exception as e:
            logger.error(
                "Failed to retrieve user profile",
                extra={
                    'user_id': user.id,
                    'email': user.email,
                    'error': str(e)
                }
            )
            raise

class CustomUserViewSet(UserViewSet):
    @action(["post"], detail=False, throttle_classes=[UserRateThrottle])
    def reset_password(self, request, *args, **kwargs):
        """
        Handles password reset requests.

        This method utilizes Djoser's built-in reset_password functionality
        to send a password reset email to the user. Rate limiting is applied
        to prevent brute force attacks on the password reset endpoint.

        """
        return super().reset_password(request, *args, **kwargs)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    """
    Class for successfull user log out
    """
    def post(self, request):
        refresh_token = request.data["refresh"]
        
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.set_exp(lifetime=timedelta(seconds=0))
            request.user.id
            print(f'{request.user.id}, {refresh_token} ')
            is_valid = is_refresh_token_valid(request.user.id, refresh_token)
            print("Is valid:", is_valid)
            delete_refresh_token(request.user.id)
        else:
            return Response({"error": "The refresh token hadn't been provided"}, status=status.HTTP_400_BAD_REQUEST)

        access_token = request.auth.token
        ac_token = AccessToken(access_token)
        ac_token.set_exp(lifetime=timedelta(seconds=0))
        is_valid = is_refresh_token_valid(request.user.id, refresh_token)
        print("Is valid:", is_valid)
        return Response({"message": "User logged out successfully"}, status=status.HTTP_200_OK)

