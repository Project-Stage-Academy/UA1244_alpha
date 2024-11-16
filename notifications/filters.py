from django_filters import FilterSet

from .models import Notification


class NotificationFilter(FilterSet):
    """Notification Filter
    
    Fields:
    - notification_type
    - status
    - delivery_status
    - investor__id
    - startup__id
    """
    class Meta:
        model = Notification
        fields = {
           'notification_type': ['exact'],
           'status': ['exact'],
           'delivery_status': ['exact'],
           'investor__id': ['exact'],
           'startup__id': ['exact'],
        }
