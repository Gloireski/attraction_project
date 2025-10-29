from django_filters import rest_framework as filters

from .models import Attraction

class AttractionFilter(filters.FilterSet):
    class Meta:
        model = Attraction
        fields = {
            'name': ['icontains'],
            'city': ['exact'],
            'category': ['exact'],
            'price_level': ['exact'],
            'rating': ['gte', 'lte'],
        }
