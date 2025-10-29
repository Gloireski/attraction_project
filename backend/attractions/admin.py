from django.contrib import admin

from django.contrib import admin
from .models import Attraction, Category

@admin.register(Attraction)
class AttractionAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'city', 'price_level', 'rating')
    list_filter = ('category', 'price_level', 'city')
    search_fields = ('name', 'description', 'city')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)

