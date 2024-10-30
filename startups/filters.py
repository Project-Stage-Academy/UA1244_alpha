import logging
import django_filters
from startups.models import StartUpProfile


logger = logging.getLogger('django')


class StartUpProfileFilter(django_filters.FilterSet):
    """
    name: Filters the startup profiles by name.
    description: Filters the startup profiles by description.
    created_at: Filters the startup profiles by creation date range.
    """

    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains', label='Startup Name')
    description = django_filters.CharFilter(field_name='description', lookup_expr='icontains', label='Description')
    created_at = django_filters.DateFromToRangeFilter(field_name='created_at', label='Creation Date Range')

    class Meta:
        model = StartUpProfile
        fields = ['name', 'description', 'created_at']

    def filter_created_at(self, queryset, name, value):
        logger.info(f"Filtering by created_at range: {value}")
        try:
            result = queryset.filter(created_at__range=value)
            logger.info(f"Filtered {result.count()} records by created_at range: {value}")
            return result
        except (ValueError, TypeError) as e:
            logger.error(f"Error filtering by created_at range: {value}, error: {str(e)}")
            raise django_filters.exceptions.ValidationError("Invalid date range format.")
