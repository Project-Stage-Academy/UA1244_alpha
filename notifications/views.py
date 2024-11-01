from django.shortcuts import render
from rest_framework import generics, filters, status
from rest_framework.permissions import IsAuthenticated
from investors.models import InvestorProfile
from django.shortcuts import get_object_or_404

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .serializers import (
   NotificationForInvestorSerializersList,
   NotificationSerializer, 
   ExtendedNotificationSerializer)
from .models import Notification, NotificationStatus
from .filters import NotificationFilter




class InvestorsNotificationsListView(generics.ListAPIView):
    """API view for get investors notifications"""

    serializer_class = NotificationForInvestorSerializersList
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        investor = get_object_or_404(InvestorProfile, user=self.request.user)
        return Notification.objects.filter(investor=investor.id).order_by('-created_at')

=======



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
    serializer_class = NotificationSerializer
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
