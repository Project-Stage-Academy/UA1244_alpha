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
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer
from datetime import timedelta

logger = logging.getLogger('users')


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def authenticate_user(self, email, password):
        """
        Authenticate a user by email and password.

        Args:
            email: User's email
            password: User's password

        Returns:
            User instance if authentication successful

        Raises:
            ValidationError: If authentication fails
        """
        logger.debug(f"Attempting to authenticate user: {email}")

        try:
            user = User.objects.get(email=email)

            if not user.check_password(password):
                logger.warning(f"Invalid password attempt for user: {email}")
                raise ValidationError("Invalid credentials")

            if not user.is_active and not user.is_soft_deleted:
                logger.info(f"Disabled account access attempt: {email}")
                raise ValidationError("Account is disabled")

            logger.info(f"Successfully authenticated user: {email}")
            return user

        except User.DoesNotExist:
            logger.warning(f"Authentication attempt for non-existent user: {email}")
            raise ValidationError("Invalid credentials")

    def generate_tokens(self, user):
        """
        Generate JWT tokens for authenticated user.

        Args:
            user: Authenticated user instance

        Returns:
            dict: Token pair and user information
        """
        logger.debug(f"Generating tokens for user: {user.email}")

        try:
            refresh = RefreshToken.for_user(user)
            tokens = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user_id': user.id,
                'email': user.email,
                'is_soft_deleted': user.is_soft_deleted
            }
            logger.info(f"Successfully generated tokens for user: {user.email}")
            return tokens

        except Exception as e:
            logger.error(f"Token generation failed for user {user.email}: {str(e)}")
            raise

    def post(self, request, *args, **kwargs):
        """
        Handle POST request for token generation.

        Args:
            request: HTTP request object

        Returns:
            Response: JWT tokens or error message
        """
        email = request.data.get('email')
        password = request.data.get('password')

        logger.debug(f"Token request received for email: {email}")

        try:
            user = self.authenticate_user(email, password)
            tokens = self.generate_tokens(user)

            logger.info(
                "Token generation successful",
                extra={
                    'user_id': user.id,
                    'email': user.email,
                    'is_soft_deleted': user.is_soft_deleted
                }
            )

            return Response(tokens, status=status.HTTP_200_OK)

        except ValidationError as e:
            logger.warning(
                "Authentication failed",
                extra={
                    'email': email,
                    'error': str(e)
                }
            )
            return Response(
                {"error": str(e)},
                status=status.HTTP_401_UNAUTHORIZED
            )

        except Exception as e:
            logger.error(
                "Unexpected error during authentication",
                extra={
                    'email': email,
                    'error': str(e)
                },
                exc_info=True
            )
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


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
            serializer = UserSerializer(request.user, context={'request': request})
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
    def get_roles(self, request):
        """
        Retrieve all roles for the authenticated user.
        """
        user = request.user
        roles = user.get_roles_display()
        return Response({"roles": roles}, status=status.HTTP_200_OK)

    @action(["get"], detail=False, permission_classes=[IsAuthenticated])
    def get_active_role(self, request):
        """
        Retrieve the current active role for the authenticated user.
        """
        user = request.user
        roles = self.get_roles(request).data.get("roles")

        active_role = user.get_active_role_display()
        return Response({"active_role": active_role, "all_roles": roles}, status=status.HTTP_200_OK)

    @action(["post"], detail=False, permission_classes=[IsAuthenticated])
    def set_active_role(self, request):
        """
        Set the active role for the authenticated user.
        """
        role_name = request.data.get('role_name')
        user = request.user
        roles = self.get_roles(request).data.get("roles")

        if role_name not in roles:
            return Response({"error": f"User does not have the role '{role_name}'"}, status=status.HTTP_400_BAD_REQUEST)

        user.set_active_role(role_name)
        return Response({"message": f"Active role set to '{role_name}'"}, status=status.HTTP_200_OK)

    @action(["post"], detail=False, permission_classes=[IsAuthenticated])
    def add_role(self, request):
        """Add a role to the user."""
        role_name = request.data.get('role_name')
        user = request.user
        logger.debug(f"Attempting to add role '{role_name}' to user {user.email}")

        if role_name == 'Admin' and not user.is_staff:
            logger.warning(
                f"Unauthorized attempt to add Admin role by user {user.email}"
            )
            return Response(
                {"error": "Only administrators can add Admin role"},
                status=status.HTTP_403_FORBIDDEN
            )


        try:
            target_user_id = request.data.get('user_id')
            if target_user_id and user.is_staff:
                target_user = User.objects.get(id=target_user_id)
            else:
                target_user = user

            target_user.add_role(role_name)
            logger.info(
                "Role successfully added to user",
                extra={
                    'user_id': target_user.id,
                    'email': target_user.email,
                    'role': role_name
                }
            )
            return Response({"message": f"Role '{role_name}' added."})
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except ValidationError as e:
            logger.error(
                "Failed to add role to user",
                extra={
                    'user_id': target_user.id,
                    'email': target_user.email,
                    'role': role_name,
                    'error': str(e)
                }
            )
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(["post"], detail=False, permission_classes=[IsAuthenticated])
    def remove_role(self, request):
        """Remove a role from the user."""
        role_name = request.data.get('role_name')
        user = request.user
        logger.debug(f"Attempting to remove role '{role_name}' from user {user.email}")

        if role_name not in user.get_roles_display():
            logger.warning(f"User  {user.email} does not have the role: {role_name}")
            raise ValidationError(f"User  {user.email} does not have the role: {role_name}")

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

