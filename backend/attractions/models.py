from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Attraction(models.Model):
    CATEGORY_CHOICES = [
        ('restaurants', 'Restaurants'),
        ('hotels', 'Hôtels'),
        ('attractions', 'Attractions'),
        ('geos', 'Sites Géographiques'),
    ]
    
    PRICE_LEVELS = [
        (1, '$'),
        (2, '$$'),
        (3, '$$$'),
        (4, '$$$$'),
    ]
    
    # TripAdvisor data
    tripadvisor_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Location
    address = models.CharField(max_length=500)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    
    # Category & Price
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    price_level = models.IntegerField(choices=PRICE_LEVELS, null=True, blank=True)
    
    # Rating
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0)
    num_reviews = models.IntegerField(default=0)
    
    # Contact
    phone = models.CharField(max_length=50, blank=True)
    website = models.URLField(blank=True)
    email = models.EmailField(blank=True)
    
    # Opening hours (stored as JSON)
    opening_hours = models.JSONField(null=True, blank=True)
    
    # Images
    photo_url = models.URLField(blank=True)
    photo_count = models.IntegerField(default=0)
    
    # Awards
    awards = models.JSONField(default=list, blank=True)
    
    # Restaurant specific
    cuisine_types = models.JSONField(default=list, blank=True)
    
    # Hotel specific
    hotel_class = models.IntegerField(null=True, blank=True)
    hotel_style = models.JSONField(default=list, blank=True)
    
    # Popularity
    likes_count = models.IntegerField(default=0)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'attractions'
        ordering = ['-likes_count', '-rating']
        indexes = [
            models.Index(fields=['country', 'city']),
            models.Index(fields=['category']),
            models.Index(fields=['-likes_count']),
        ]
    
    def __str__(self):
        return self.name