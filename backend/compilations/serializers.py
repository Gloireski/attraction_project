from rest_framework import serializers
from .models import Compilation, CompilationItem
from attractions.serializers import AttractionListSerializer
from attractions.models import Attraction

class CompilationItemSerializer(serializers.ModelSerializer):
    attraction = AttractionListSerializer(read_only=True)
    attraction_id = serializers.PrimaryKeyRelatedField(
        queryset=Attraction.objects.all(),
        source='attraction',
        write_only=True
    )
    
    class Meta:
        model = CompilationItem
        fields = ['id', 'attraction', 'attraction_id', 'order', 'estimated_cost', 'notes', 'added_at']


class CompilationSerializer(serializers.ModelSerializer):
    items = CompilationItemSerializer(many=True, read_only=True)
    items_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Compilation
        fields = ['id', 'name', 'sort_by', 'total_budget', 'items', 'items_count', 'created_at', 'updated_at']
    
    def get_items_count(self, obj):
        return obj.items.count()