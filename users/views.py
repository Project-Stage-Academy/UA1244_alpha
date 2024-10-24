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

logger = logging.getLogger('users')


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Obtains a token pair for a user.
    """
    serializer_class = TokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        """
        Handles the POST request for token generation.
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

            return Response({
                'refresh': str(tokens['refresh']),
                'access': str(tokens['access']),
                'user_id': user.id,
                'email': user.email,
            }, status=status.HTTP_200_OK)

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
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Handles the GET request for user profile.
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



