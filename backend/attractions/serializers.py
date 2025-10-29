from rest_framework import serializers
from .models import Attraction, Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class AttractionSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    class Meta:
        model = Attraction
        fields = '__all__'
