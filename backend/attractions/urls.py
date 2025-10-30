# backend/attractions/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import home, get_attractions, get_location_details, get_categories, AttractionViewSet, sync_from_tripadvisor
from .views import attractions_popular, attractions_search, attractions_list, attraction_detail

# from .views import AttractionViewSet, UserProfileViewSet, CompilationViewSet

router = DefaultRouter()

router.register(r'attractions', AttractionViewSet, basename='attraction')
# router.register(r'profiles', UserProfileViewSet, basename='profile')
# router.register(r'compilations', CompilationViewSet, basename='compilation'

urlpatterns = [
    path('', home, name='api-home'),
    path('attractions_v1/', get_attractions, name='attractions'),
    path('attractions/<int:location_id>/', get_location_details, name='attraction-detail'),
    path('attractions_v1/popular/', attractions_popular, name='attractions-popular'),
    path('attractions_v1/list/', attractions_list, name='attractions-list'),
    path('attractions_v1/search/', attractions_search, name='attractions-search'),
    path('attractions_v1/<int:pk>/', attraction_detail, name='attraction-detail'),
    path('attractions_v1/sync_tripadvisor/', sync_from_tripadvisor, name='sync_tripadvisor'),
    path('categories/', get_categories, name='categories'),
    path("tripadvisor/search/", views.search_tripadvisor, name="search_tripadvisor"),
    path('', include(router.urls)),
    
]
