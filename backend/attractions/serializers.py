from rest_framework import serializers
from .models import Attraction, Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class AttractionSerializer(serializers.ModelSerializer):
    distance = serializers.SerializerMethodField()
    
    class Meta:
        model = Attraction
        fields = '__all__'
    
    def get_distance(self, obj):
        # Calculate distance from user location if provided in context
        return None

class AttractionListSerializer(serializers.ModelSerializer):
    """Lighter serializer for list views"""
    class Meta:
        model = Attraction
        fields = [
            'id', 'tripadvisor_id', 'name', 'city', 'country',
            'category', 'price_level', 'rating', 'num_reviews',
            'photo_url', 'likes_count', 'latitude', 'longitude'
        ]
