from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import generics, filters, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Notification, NotificationStatus
from .serializers import NotificationSerializer
from .filters import NotificationFilter


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


class NotificiationByIDView(generics.RetrieveUpdateDestroyAPIView):
    """API view to GET, UPDADE, DELETE notification by id"""
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'

    def update(self, request, *args, **kwargs):
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
            data = {
                'message': 'Notification updated successfully',
                'notification': serializer.data,
                'associated_profile_url': notification.get_associated_profile_url()
            }
            response = Response(data, status=status.HTTP_200_OK)

        else:
            response = Response(
                {'detail': 'No valid fields to update'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return response

    def get(self, *args, **kwargs):
        notification = self.get_object()
        serializer = self.get_serializer(notification)
        data = {
            "message": "Notification updated successfully",
            "notification": serializer.data,
            "associated_profile_url": notification.get_associated_profile_url()
        }
        return Response(data, status=status.HTTP_200_OK)