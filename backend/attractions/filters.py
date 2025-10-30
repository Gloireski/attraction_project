from django_filters import rest_framework as filters
from django.db.models import Q
from .models import Attraction
from math import radians, cos, sin, asin, sqrt

class AttractionFilter(filters.FilterSet):
    min_rating = filters.NumberFilter(field_name='rating', lookup_expr='gte')
    max_rating = filters.NumberFilter(field_name='rating', lookup_expr='lte')
    min_reviews = filters.NumberFilter(field_name='num_reviews', lookup_expr='gte')
    min_photos = filters.NumberFilter(field_name='photo_count', lookup_expr='gte')
    search = filters.CharFilter(method='filter_search')
    profile_type = filters.CharFilter(method='filter_profile_type')
    latitude = filters.NumberFilter(method='filter_by_radius')
    longitude = filters.NumberFilter(method='filter_by_radius')
    radius = filters.NumberFilter(method='filter_by_radius')  # in km
    price_level = filters.NumberFilter(field_name='price_level', lookup_expr='exact')

    class Meta:
        model = Attraction
        fields = {
            'category': ['exact'],
            'city': ['exact'],
            'country': ['exact'],
        }

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value) |
            Q(city__icontains=value) |
            Q(address__icontains=value)
        )

    def filter_profile_type(self, queryset, name, value):
        if value == 'local':
            queryset = queryset.exclude(category='hotel')
        elif value == 'professional':
            queryset = queryset.filter(Q(category='restaurant') | Q(category='hotel'))
        return queryset

    def filter_by_radius(self, queryset, name, value):
        lat = self.data.get('latitude')
        lng = self.data.get('longitude')
        radius = self.data.get('radius', 10)
        if lat and lng:
            lat = float(lat)
            lng = float(lng)
            radius = float(radius)
            
            def haversine(lon1, lat1, lon2, lat2):
                lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
                dlon = lon2 - lon1
                dlat = lat2 - lat1
                a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
                c = 2 * asin(sqrt(a))
                km = 6371 * c
                return km

            filtered_ids = [
                a.id for a in queryset
                if haversine(lng, lat, float(a.longitude), float(a.latitude)) <= radius
            ]
            queryset = queryset.filter(id__in=filtered_ids)
        return queryset
