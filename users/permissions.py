from django.core.exceptions import PermissionDenied
from functools import wraps


def role_required(role_name):
    """
    Decorator to check if the user has the required active role.

    :param role_name: The name of the role required for access.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.active_role or request.user.active_role.name != role_name:
                raise PermissionDenied("You do not have permission to access this resource.")
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

