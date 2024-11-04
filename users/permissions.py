import logging
from rest_framework import permissions
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from investment_tracking.models import InvestmentTracking

logger = logging.getLogger('users')


class DetailedPermissionLogging(permissions.BasePermission):

    log_prefix = "DetailedPermissionLogging"
    AUTH_HEADER_KEY = getattr(settings, 'AUTH_HEADER_KEY', 'HTTP_AUTHORIZATION')

    log_methods = {
        'debug': logger.debug,
        'info': logger.info,
        'warning': logger.warning,
        'error': logger.error
    }

    def get_base_log_data(self, request, view) -> dict:
        """Generates basic information for logging"""
        return {
            'ip': request.META.get('REMOTE_ADDR'),
            'path': request.path,
            'method': request.method,
            'view': view.__class__.__name__,
            'timestamp': timezone.now().isoformat(),
            'user_id': getattr(request.user, 'id', None)
        }

    def log_event(self, level: str, message: str, extra_data: dict) -> None:
        """Centralized event logging with level mapping"""
        log_method = self.log_methods.get(level, logger.info)
        log_method(
            f'{self.log_prefix}: {message}',
            extra={'extra_data': extra_data},
            exc_info=(level == 'error')
        )

    def has_permission(self, request, view) -> bool:
        """General rights check"""
        base_log_data = self.get_base_log_data(request, view)

        # 1. Authentication check
        if not request.user.is_authenticated:
            self.log_event('warning', 'Unauthenticated access attempt', {
                **base_log_data,
                'reason': 'not_authenticated'
            })
            return False

        # 2. Token check
        auth_header = request.META.get(self.AUTH_HEADER_KEY, '')
        if auth_header:
            auth_type = auth_header.split()[0] if ' ' in auth_header else auth_header
            self.log_event('info', 'Token authentication', {
                **base_log_data,
                'auth_type': auth_type
            })

        return True

    def has_object_permission(self, request, view, obj) -> bool:
        """Checking rights to a specific object"""
        try:
            base_log_data = {
                **self.get_base_log_data(request, view),
                'object_id': getattr(obj, 'id', None),
                'object_type': obj.__class__.__name__
            }

            # 1. Owner verification
            if hasattr(obj, 'user'):
                is_owner = obj.user == request.user
                owner_id = getattr(obj.user, 'id', None)
                self.log_event('info', 'Ownership check', {
                    **base_log_data,
                    'is_owner': is_owner,
                    'object_owner_id': owner_id
                })
                if is_owner:
                    return True

            # 2. Checking groups
            user_groups = list(request.user.groups.values_list('name', flat=True))
            self.log_event('info', 'Group permission check', {
                **base_log_data,
                'user_groups': user_groups
            })

            # 3. Checking staff status
            if request.user.is_staff:
                self.log_event('info', 'Staff access granted', {
                    **base_log_data,
                    'permission_type': 'staff'
                })
                return True

            self.log_event('warning', 'Access denied', {
                **base_log_data,
                'reason': 'insufficient_permissions'
            })
            return False

        except Exception as e:
            self.log_event('error', 'Permission check failed', {
                **base_log_data,
                'error': str(e)
            })
            return False


class InvestmentPermission(DetailedPermissionLogging):
    """Verification based on the existence of investments"""

    def has_permission(self, request, view) -> bool:
        if not super().has_permission(request, view):
            return False

        investor_profile = getattr(request.user, 'investorprofile', None)
        if not investor_profile:
            self.log_event('warning', 'No investor profile found', {
                'user_id': request.user.id,
                'reason': 'no_investor_profile'
            })
            return False

        base_log_data = self.get_base_log_data(request, view)

        try:
            investment_exists = InvestmentTracking.objects.filter(
                investor=investor_profile,
                startup_id=view.kwargs.get('startup_id')  #if /startups/<int:startup_id>/!
            ).exists()

            if investment_exists:
                self.log_event('info', 'Investment found', {
                    **base_log_data,
                    'investor_id': investor_profile.id
                })
                return True
            else:
                self.log_event('warning', 'No investment found', {
                    **base_log_data,
                    'investor_id': investor_profile.id,
                    'reason': 'no_investment'
                })
                return False

        except ObjectDoesNotExist:
            self.log_event('error', 'Investment check failed', {
                'user_id': request.user.id,
                'error': 'InvestmentTracking entry not found'
            })
            return False
        except Exception as e:
            self.log_event('error', 'Unexpected error during investment check', {
                'user_id': request.user.id,
                'error': str(e)
            })
            return False