# backend/attractions/urls.py
from django.urls import path
from . import views
from .views import get_attractions, get_categories

urlpatterns = [
    path('', views.home, name='shop-home'),
    path('attractions/', get_attractions, name='attractions'),
    path('categories/', get_categories, name='categories'),
]
