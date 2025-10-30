from rest_framework import serializers
from .models import UserProfile

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id', 'session_key', 'profile_type', 'country', 'created_at']
        read_only_fields = ['session_key', 'created_at']