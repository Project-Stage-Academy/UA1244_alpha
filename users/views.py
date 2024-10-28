import logging
from djoser.views import UserViewSet
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import UserRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.response import Response
from rest_framework import status
from .models import User
from .serializers import UserSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from datetime import timedelta

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

    @action(["get"], detail=False, permission_classes=[IsAuthenticated])
    def get_active_role(self, request):
        """
        Retrieve the current active role for the authenticated user.
        """
        user = request.user
        logger.debug(f"Retrieving active role for user {user.email}")

        try:
            active_role = user.get_active_role_display()
            logger.info(
                "Active role successfully retrieved",
                extra={
                    'user_id': user.id,
                    'email': user.email,
                    'active_role': active_role
                }
            )
            return Response({
                "active_role": active_role
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(
                "Failed to retrieve active role",
                extra={
                    'user_id': user.id,
                    'email': user.email,
                    'error': str(e)
                }
            )
            return Response(
                {"error": "Failed to retrieve active role"},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(["get"], detail=False, permission_classes=[IsAuthenticated])
    def get_roles(self, request):
        """
        Retrieve all roles for the authenticated user.

        :param request: The incoming request.
        :return: A response containing the user's roles.
        """
        user = request.user
        roles = user.get_roles_display()
        return Response({"roles": roles}, status=status.HTTP_200_OK)

    @action(["post"], detail=False, permission_classes=[IsAuthenticated])
    def add_role(self, request):
        """Add a role to the user."""
        role_name = request.data.get('role_name')
        user = request.user
        logger.debug(f"Attempting to add role '{role_name}' to user {user.email}")

        try:
            user.add_role(role_name)
            logger.info(
                "Role successfully added to user",
                extra={
                    'user_id': user.id,
                    'email': user.email,
                    'role': role_name
                }
            )
            return Response({"message": f"Role '{role_name}' added."})
        except ValidationError as e:
            logger.error(
                "Failed to add role to user",
                extra={
                    'user_id': user.id,
                    'email': user.email,
                    'role': role_name,
                    'error': str(e)
                }
            )
            return Response({"error": str(e)}, status=400)

    @action(["post"], detail=False, permission_classes=[IsAuthenticated])
    def remove_role(self, request):
        """Remove a role from the user."""
        role_name = request.data.get('role_name')
        user = request.user
        logger.debug(f"Attempting to remove role '{role_name}' from user {user.email}")

        try:
            user.remove_role(role_name)
            logger.info(
                "Role successfully removed from user",
                extra={
                    'user_id': user.id,
                    'email': user.email,
                    'role': role_name
                }
            )
            return Response({"message": f"Role '{role_name}' removed."})
        except ValidationError as e:
            logger.error(
                "Failed to remove role from user",
                extra={
                    'user_id': user.id,
                    'email': user.email,
                    'role': role_name,
                    'error': str(e)
                }
            )
            return Response({"error": str(e)}, status=400)

    @action(["post"], detail=False, permission_classes=[IsAuthenticated])
    def soft_delete(self, request):
        """Soft delete user account."""
        user = request.user
        logger.debug(f"Attempting to soft delete user account: {user.email}")

        try:
            user.soft_delete()
            logger.info(
                "User account successfully soft deleted",
                extra={
                    'user_id': user.id,
                    'email': user.email
                }
            )
            return Response({"message": "Account successfully deleted."})
        except ValidationError as e:
            logger.error(
                "Failed to soft delete user account",
                extra={
                    'user_id': user.id,
                    'email': user.email,
                    'error': str(e)
                }
            )
            return Response({"error": str(e)}, status=400)

    @action(["post"], detail=False, permission_classes=[IsAuthenticated])
    def reactivate(self, request):
        """Reactivate soft-deleted account."""
        user = request.user
        logger.debug(f"Attempting to reactivate user account: {user.email}")

        try:
            user.reactivate()
            logger.info(
                "User account successfully reactivated",
                extra={
                    'user_id': user.id,
                    'email': user.email
                }
            )
            return Response({"message": "Account successfully reactivated."})
        except ValidationError as e:
            logger.error(
                "Failed to reactivate user account",
                extra={
                    'user_id': user.id,
                    'email': user.email,
                    'error': str(e)
                }
            )
            return Response({"error": str(e)}, status=400)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    """
    Class for successfull user log out
    """
    def post(self, request):
        refresh_token = request.data.get("refresh")
        user = request.user
        logger.debug(f"Logout attempt for user: {user.email}")

        if refresh_token:
            token = RefreshToken(refresh_token)
            token.set_exp(lifetime=timedelta(seconds=0))
        else:
            logger.error(
                "Logout failed: refresh token not provided",
                extra={'user_id': user.id, 'email': user.email}
            )
            return Response({"error": "The refresh token hadn't been provided"}, status=status.HTTP_400_BAD_REQUEST)

        access_token = request.auth.token
        ac_token = AccessToken(access_token)
        ac_token.set_exp(lifetime=timedelta(seconds=0))

        logger.info(
            "User successfully logged out",
            extra={'user_id': user.id, 'email': user.email}
        )

        return Response({"message": "User logged out successfully"}, status=status.HTTP_200_OK)

