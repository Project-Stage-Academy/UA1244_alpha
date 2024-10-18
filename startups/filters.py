import django_filters
from startups.models import StartUpProfile


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
        try:
            return queryset.filter(created_at__range=value)
        except (ValueError, TypeError):
            raise django_filters.exceptions.ValidationError("Invalid date range format.")
