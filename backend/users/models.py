from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    PROFILE_TYPES = [
        ('local', 'Local'),
        ('tourist', 'Touriste'),
        ('professional', 'Professionnel'),
    ]
    
    session_key = models.CharField(max_length=255, unique=True)
    profile_type = models.CharField(max_length=20, choices=PROFILE_TYPES)
    country = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_profiles'
        
    def __str__(self):
        return f"{self.profile_type} - {self.country}"