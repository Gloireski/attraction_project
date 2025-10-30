from django.db import models
from users.models import UserProfile
from attractions.models import Attraction

class Compilation(models.Model):
    SORT_CHOICES = [
        ('budget_asc', 'Budget croissant'),
        ('budget_desc', 'Budget décroissant'),
        ('distance', 'Distance optimale'),
    ]
    
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='compilations')
    name = models.CharField(max_length=255, default='Ma compilation')
    sort_by = models.CharField(max_length=20, choices=SORT_CHOICES, default='distance')
    total_budget = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'compilations'
    
    def __str__(self):
        return f"{self.name} - {self.user_profile.profile_type}"


class CompilationItem(models.Model):
    compilation = models.ForeignKey(Compilation, on_delete=models.CASCADE, related_name='items')
    attraction = models.ForeignKey(Attraction, on_delete=models.CASCADE)
    order = models.IntegerField(default=0)
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'compilation_items'
        ordering = ['order']
        unique_together = ['compilation', 'attraction']
    
    def __str__(self):
        return f"{self.compilation.name} - {self.attraction.name}"