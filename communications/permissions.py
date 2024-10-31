from rest_framework.permissions import BasePermission


class IsOwnerOrRecipient(BasePermission):
    """
    Custom permission to allow only the sender or recipient to access the messages.
    """
    def has_object_permission(self, request, view, obj):
        return obj.sender_id == request.user.id or obj.receiver_id == request.user.id
