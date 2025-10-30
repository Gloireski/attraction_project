from django_filters import rest_framework as filters
from django.db.models import Q
from .models import Attraction


class AttractionFilter(filters.FilterSet):
    # Extra filters for more dynamic queries
    min_rating = filters.NumberFilter(field_name='rating', lookup_expr='gte')
    max_rating = filters.NumberFilter(field_name='rating', lookup_expr='lte')
    min_reviews = filters.NumberFilter(field_name='num_reviews', lookup_expr='gte')
    min_photos = filters.NumberFilter(field_name='photo_count', lookup_expr='gte')
    search = filters.CharFilter(method='filter_search')
    profile_type = filters.CharFilter(method='filter_profile_type')

    class Meta:
        model = Attraction
        fields = {
            'category': ['exact'],
            'city': ['exact'],
            'country': ['exact'],
            'price_level': ['exact'],
        }

    def filter_search(self, queryset, name, value):
        """Custom global search filter"""
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value) |
            Q(city__icontains=value) |
            Q(address__icontains=value)
        )

    def filter_profile_type(self, queryset, name, value):
        """Filter based on profile type (local, professional, etc.)"""
        if value == 'local':
            queryset = queryset.exclude(category='hotel')
        elif value == 'professional':
            queryset = queryset.filter(Q(category='restaurant') | Q(category='hotel'))
        return queryset
