import logging
from django.forms import ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from rest_framework import generics, filters, status

from rest_framework import generics, filters, status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework.exceptions import NotFound

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from investors.models import InvestorProfile
from startups.models import StartUpProfile
from users.models import Role
from .models import (
    Notification,
    NotificationStatus,
    NotificationPreferences,
    RolesNotifications
)
from .serializers import (
    NotificationSerializer,
    ExtendedNotificationSerializer,
    NotificationPreferencesSerializer,
    RolesNotificationsSerializer,
    NotificationSerializerPost, NotificationForInvestorSerializersList
)
from .filters import NotificationFilter


User = get_user_model()
logger = logging.getLogger('django')


class InvestorsNotificationsListView(generics.ListAPIView):
    """API view for get investors notifications"""

    serializer_class = NotificationForInvestorSerializersList
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        investor = get_object_or_404(InvestorProfile, user=self.request.user)
        return Notification.objects.filter(investor=investor.id).order_by('-created_at')


User = get_user_model()
logger = logging.getLogger('__name__')


class NotificationListView(generics.ListAPIView):
    """API view for all Notifications
    
    Filter fields:
    - notification_type
    - status
    - delivery_status
    - investor__id
    - startup__id

    Ordering fields:
    - sent_at (default)
    - read_at
    """
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializerPost
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination
    filterset_class = NotificationFilter
    ordering_fields = ['sent_at', 'read_at']
    ordering = ['sent_at']

    @swagger_auto_schema(
        operation_description='Notifications list with filters',
        responses={
            status.HTTP_200_OK: NotificationSerializer,
            status.HTTP_400_BAD_REQUEST: openapi.Response('Bad Request'),
            status.HTTP_401_UNAUTHORIZED: openapi.Response('Unauthorized'),
            status.HTTP_404_NOT_FOUND: openapi.Response('Not Found')
        },
        manual_parameters=[
            openapi.Parameter(
                'notification_type', openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                description='1 - Follow, 2 - Message, 3 - Update', enum=[1, 2, 3]
            ),
            openapi.Parameter(
                'status', openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                description='0 - Unread, 1 - Read', enum=[0, 1]
            ),
            openapi.Parameter(
                'delivery_status', openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                description='0 - Failed, 1 - Sent', enum=[0, 1]
            ),
            openapi.Parameter(
                'ordering', openapi.IN_QUERY, type=openapi.TYPE_STRING,
                description='by sent_at, -sent_at, read_at, -read_at',
                enum=['sent_at', '-sent_at', 'read_at', '-read_at']
            ),
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class NotificiationByIDView(generics.RetrieveDestroyAPIView):
    """API view to GET, PATCH, DELETE notification by id"""
    queryset = Notification.objects.all()
    serializer_class = ExtendedNotificationSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'

    @swagger_auto_schema(
        operation_description='Patch Notification status field',
        responses={
            status.HTTP_200_OK: ExtendedNotificationSerializer,
            status.HTTP_400_BAD_REQUEST: 'Bad Request - Invalid Status',
            status.HTTP_404_NOT_FOUND: 'Not Found - No Notification matches the given query'
        },
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'status': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description='0 - Unread, 1 - Read',
                    enum=[0, 1]
                )
            }
        ),
    )
    def patch(self, request, *args, **kwargs):
        """notification status patch method"""
        notification = self.get_object()
        if 'status' in request.data:
            update_status = int(request.data['status'])
            if update_status not in (
                    NotificationStatus.READ, NotificationStatus.UNREAD):
                return Response(
                    {'detail': 'Invalid status'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            notification.set_read_status(read=update_status)
            clear_read_at = update_status == NotificationStatus.UNREAD
            notification.set_read_at(clear_=clear_read_at)
            notification.save()

            serializer = self.get_serializer(notification)
            response = Response(serializer.data, status=status.HTTP_200_OK)

        else:
            response = Response(
                {'detail': 'Bad Request'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return response

    @swagger_auto_schema(
        operation_description='Get Notification by id',
        responses={
            status.HTTP_200_OK: ExtendedNotificationSerializer,
            status.HTTP_400_BAD_REQUEST: 'Bad Request - Invalid Status',
            status.HTTP_404_NOT_FOUND: 'Not Found - No Notification matches the given query'
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description='Delete Notification by id',
        responses={
            status.HTTP_204_NO_CONTENT: 'Successfully deleted',
            status.HTTP_404_NOT_FOUND: 'Not Found - No Notification matches the given query'
            }
        )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class RolesNotificationsListCreateView(generics.ListCreateAPIView):
    """API view to GET and CREATE (assign) notification types to roles"""
    queryset = RolesNotifications.objects.all()
    serializer_class = RolesNotificationsSerializer
    permission_classes = [IsAuthenticated]


class RoleNotificationsByIDView(generics.RetrieveDestroyAPIView):
    """API view to GET and DELETE role-notification pairs by id"""
    queryset = RolesNotifications.objects.all()
    serializer_class = RolesNotificationsSerializer
    permission_classes = [IsAuthenticated]


class RoleMixin:
    def get_user_role_profile(self):
        role = profile = user = None
        try:
            if 'startup' in self.request.path:
                role = Role.objects.get(name='Startup')
                profile = StartUpProfile.objects.get(id=self.kwargs.get('pk'))
            elif 'investor' in self.request.path:
                role = Role.objects.get(name='Investor')
                profile = InvestorProfile.objects.get(id=self.kwargs.get('pk'))
            if role and profile:
                user_id = profile.get_user().id
                user = User.objects.get(id=user_id)

        except (Role.DoesNotExist, StartUpProfile.DoesNotExist, 
                InvestorProfile.DoesNotExist) as e:
            logger.error(f'Role, Startup or Investor not found: {e}')

        return {
            'user': user,
            'role': role,
            'profile': profile
            }


class ProfileNotificationSettingsView(RoleMixin, generics.ListAPIView):
    """API view to GET all Notification Preferences for Profile"""
    queryset = NotificationPreferences.objects.all()
    serializer_class = NotificationPreferencesSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        profile_info = self.get_user_role_profile()
        user = profile_info['user']
        role = profile_info['role']
        if user and user.id == self.request.user.id:
            notification_preferences = NotificationPreferences.objects.filter(
                user=user.id,
                role=role
            )
            return notification_preferences
        raise PermissionDenied('No permission to access the user\'s notification preferences')
    
    @swagger_auto_schema(
        operation_description='Get Notification Preferences for specific profile',
        responses={
            status.HTTP_200_OK: NotificationPreferencesSerializer,
            status.HTTP_403_FORBIDDEN: 
            'Invalid user id: No permission to access the user\'s notification preferences',
        }
    )
    def get(self, request, *args, **kwargs):
        try:
            notification_preferences = self.get_queryset()
            serializer = self.get_serializer(notification_preferences, many=True)
            return Response(
                serializer.data, status=status.HTTP_200_OK
            )
        except PermissionDenied as e:
            return Response(
                {'message': f'Invalid user id: {e}'},
                status=status.HTTP_403_FORBIDDEN
            )
    

class ProfileNotificationSettingsByIDView(RoleMixin, generics.RetrieveUpdateAPIView):
    """API View to get specific Notification preference for Profile by ID"""
    queryset = NotificationPreferences.objects.all()
    serializer_class = NotificationPreferencesSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'

    def get_object(self):
        profile_info = self.get_user_role_profile()
        user = profile_info['user']
        role = profile_info['role']
        if user and user.id == self.request.user.id:
            try:
                notification_preference = NotificationPreferences.objects.get(
                    user=user.id,
                    role=role,
                    notification_type=self.kwargs.get('notification_type')
                )
            except NotificationPreferences.DoesNotExist as e:
                logger.error(f'NotificationPreferences not found for User {user}, {role}, {e}')
                raise NotFound('NotificationPreferences object not found')
            return notification_preference
        raise PermissionDenied('No permission to access the user\'s notification preferences')
    
    @swagger_auto_schema(
        operation_description='Get specific Notification Preference by ID for specific profile',
        responses={
            status.HTTP_200_OK: NotificationPreferencesSerializer,
            status.HTTP_403_FORBIDDEN: 
            'Invalid user id: No permission to access the user\'s notification preferences',
            status.HTTP_404_NOT_FOUND: 'NotificationPreferences object not found',
        }
    )
    def get(self, request, *args, **kwargs):
        try:
            notification_preference = self.get_object()
            serializer = self.get_serializer(notification_preference)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except PermissionDenied as e:
            return Response(
                {'message': f'Invalid user id: {e}'},
                status=status.HTTP_403_FORBIDDEN
            )
        except NotFound as e:
            return Response(
                {'message': e},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @swagger_auto_schema(
        operation_description='Update specific Notification Preference by ID for specific profile',
        responses={
            status.HTTP_200_OK: NotificationPreferencesSerializer,
            status.HTTP_400_BAD_REQUEST: 'Bad request: Validation error',
            status.HTTP_400_BAD_REQUEST: 'Invalid notification type for this role',
            status.HTTP_404_NOT_FOUND: 'NotificationPreferences object not found',
        }
    )
    def update(self, request, *args, **kwargs):
        notification_type = self.kwargs.get('notification_type')
        notification_preference = self.get_object()
        if notification_preference.check_notification_type(notification_type):
            serializer = self.get_serializer(notification_preference, request.data)
            try:
                serializer.is_valid()
                self.perform_update(serializer)
                return Response(
                    serializer.data,
                    status=status.HTTP_200_OK
                )
            except ValidationError as e:
                return Response(
                    {
                        'message': 'Validation error',
                        'errors': e.details
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(
                {'message': 'Invalid notification type for this role'},
                status=status.HTTP_400_BAD_REQUEST
            )


class NotificationPreferencesListView(generics.ListAPIView):
    """API View to get all Notification Preferences"""
    queryset = NotificationPreferences.objects.all()
    serializer_class = NotificationPreferencesSerializer


class ProfileNotificationsListView(RoleMixin, generics.ListAPIView):
    """API View to GET all notifications for current profile"""
    queryset = Notification
    serializer_class = ExtendedNotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        profile_id = self.kwargs.get('pk')
        profile_info = self.get_user_role_profile()
        user = profile_info['user']
        role = profile_info['role']
        profile = profile_info['profile']

        if user and user.id == self.request.user.id:
            
            if role and profile:
                recipient_field = 'investor_id' if isinstance(profile, InvestorProfile)\
                    else 'startup_id'
                notifications = Notification.objects.filter(
                    **{recipient_field: profile_id}
                )
                if notifications.exists():
                    notification_preferences = NotificationPreferences.objects.filter(
                        user_id=user.id,
                        role_id=role.id
                    )
                    preferences = (
                        preference.notification_type
                        for preference in notification_preferences
                        if preference.in_app == True
                    )
                    notifications = notifications.filter(notification_type__in=preferences)
            return notifications
        raise PermissionDenied('No permission to access the user\'s notification preferences')
    
    @swagger_auto_schema(
        operation_description='Get Notifications for specific profile',
        responses={
            status.HTTP_200_OK: NotificationPreferencesSerializer,
            status.HTTP_400_BAD_REQUEST: 'Bad request: Validation error',
            status.HTTP_403_FORBIDDEN: 
            'Invalid user id: No permission to access the user\'s notification preferences',
        }
    )
    def get(self, request, *args, **kwargs):
        try:
            notification_preferences = self.get_queryset()
            serializer = self.get_serializer(notification_preferences, many=True)
            return Response(
                serializer.data, status=status.HTTP_200_OK
            )
        except PermissionDenied as e:
            return Response(
                {'message': f'Invalid user id: {e}'},
                status=status.HTTP_403_FORBIDDEN
            )
