import os
import threading
import time
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from django.http import HttpResponse

from config import settings
from .filters import AttractionFilter
from .models import Attraction
from .serializers import AttractionSerializer
import requests
from django.http import JsonResponse

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q
from math import radians, cos, sin, asin, sqrt

from .models import Attraction
from .serializers import (
    AttractionSerializer, AttractionListSerializer
)
from .services import TripAdvisorService
from .utils import tripadvisor_category

START_TIME = time.time()

def filter_by_radius(queryset, lat, lng, radius):
    """Filter attractions within radius using Haversine formula"""
    def haversine(lon1, lat1, lon2, lat2):
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        km = 6371 * c
        return km

    filtered_ids = []
    for attraction in queryset:
        distance = haversine(float(lng), float(lat),
                             float(attraction.longitude), float(attraction.latitude))
        if distance <= radius:
            filtered_ids.append(attraction.id)

    return queryset.filter(id__in=filtered_ids)

def filter_attractions(request, queryset):
    """Apply filters from query params to queryset"""
    # profile_type filter
    profile_type = request.GET.get('profile_type')
    if profile_type:
        if profile_type == 'local':
            queryset = queryset.exclude(category='hotel')
        elif profile_type == 'professional':
            queryset = queryset.filter(Q(category='restaurant') | Q(category='hotel'))

    # min_reviews filter
    min_reviews = request.GET.get('min_reviews')
    if min_reviews:
        queryset = queryset.filter(num_reviews__gte=int(min_reviews))

    # min_photos filter
    min_photos = request.GET.get('min_photos')
    if min_photos:
        queryset = queryset.filter(photo_count__gte=int(min_photos))

    # radius filter
    lat = request.GET.get('latitude')
    lng = request.GET.get('longitude')
    radius = float(request.GET.get('radius', 10))
    if lat and lng:
        queryset = filter_by_radius(queryset, float(lat), float(lng), radius)

    return queryset

def sync_attractions_to_db(results):
    """Background task to save TripAdvisor results to local DB"""
    for result in results:
        location_id = result.get('location_id')
        details = TripAdvisorService().get_location_details(location_id)
        if details:
            Attraction.objects.update_or_create(
                tripadvisor_id=location_id,
                defaults={
                    'name': details.get('name', ''),
                    'description': details.get('description', ''),
                    'category': details.get('category', 'unknown'),
                    'city': result.get('address_obj', {}).get('city', ''),
                    'country': result.get('address_obj', {}).get('country', ''),
                    'latitude': details.get('latitude', 0.0),
                    'longitude': details.get('longitude', 0.0),
                    'rating': details.get('rating', 0),
                    'num_reviews': details.get('num_reviews', 0),
                    'photo_count': details.get('photo_count', 0),
                    'website': details.get('website', ''),
                    'phone': details.get('phone', ''),
                    'photo_url': details.get('rating_image_url', ''),
                }
            )

@api_view(['GET'])
def home(request):
    uptime_seconds = int(time.time() - START_TIME)
    uptime = f"{uptime_seconds // 3600}h {(uptime_seconds % 3600) // 60}m"

    return JsonResponse({
        "project": {
            "name": "Django IPSSI Travel Project",
            "version": "1.0.0",
            "description": "Backend for travel app fetching TripAdvisor data"
        },
        "server": {
            "environment": os.environ.get("DJANGO_ENV", "development"),
            "host": "127.0.0.1",
            "port": 8000,
            "uptime": uptime
        },
        "api_endpoints": [
            {"path": "/api/attractions/", "method": "GET", "description": "Search attractions"},
            {"path": "/api/attractions/<id>/", "method": "GET", "description": "Get attraction details"}
        ],
        "dependencies": [
            "Django 4.2",
            "djangorestframework",
            "requests",
            "django-cors-headers"
        ]
    })

@api_view(['GET'])
def get_attractions(request):
    filterset = AttractionFilter(request.GET, queryset=Attraction.objects.all())
    if filterset.is_valid():
        serializer = AttractionSerializer(filterset.qs, many=True)
        return Response(serializer.data)
    return Response(filterset.errors, status=400)

@api_view(['GET'])
def get_location_details(request, location_id):
    """
    Fetch details of a specific attraction by its ID
    """
    query_params = {
        # "locationId": location_id,
        "language": "en",
        "key": settings.TRIPADVISOR_API_KEY
    }
    headers = {
        "accept": "application/json",
    }
    url = f"https://api.content.tripadvisor.com/api/v1/location/{location_id}/details"
    r = requests.get(url, headers=headers, params=query_params)
    if r.status_code == 200:
        return JsonResponse(r.json(), safe=False)
    else:
        return JsonResponse({"error": "Attraction not found"}, status=404)

@api_view(['GET'])
def get_categories(request):
    categories = Attraction.objects.values_list('category', flat=True).distinct()
    data = [{"id": idx + 1, "name": cat} for idx, cat in enumerate(categories)]
    return Response(data)

@api_view(['GET'])
def attractions_list(request):
    queryset = Attraction.objects.all()
    queryset = filter_attractions(request, queryset)
    serializer = AttractionListSerializer(queryset, many=True)
    print("Attractions")
    return Response(serializer.data)

@api_view(['GET'])
def attractions_search(request):
    """
    Search attractions with multiple filters.
    Fallback to TripAdvisor API if local DB is empty.
    """
    print("search params:", request.GET)
    queryset = Attraction.objects.all()
    filterset = AttractionFilter(request.GET, queryset=queryset)

    if filterset.is_valid():
        filtered_qs = filterset.qs

        if not filtered_qs.exists():
            # No local results, fetch from TripAdvisor
            service = TripAdvisorService()
            query = request.GET.get('city') or request.GET.get('country') or 'World'
            category = request.GET.get('category')
            results = service.search_location(query=query, category=category)

            # Return TripAdvisor results immediately
            serializer_data = []
            for result in results:
                serializer_data.append({
                    'name': result.get('name', ''),
                    'city': result.get('address_obj', {}).get('city', ''),
                    'country': result.get('address_obj', {}).get('country', ''),
                    'tripadvisor_id': result.get('location_id'),
                    'category': result.get('category', ''),
                })

            # Start background thread to update local DB
            threading.Thread(target=sync_attractions_to_db, args=(results,), daemon=True).start()

            return Response(serializer_data)

        # Return local DB results if found
        serializer = AttractionListSerializer(filtered_qs, many=True)
        return Response(serializer.data)

    return Response(filterset.errors, status=400)

@api_view(['GET'])
def attraction_detail(request, pk):
    """
    Get detailed information about a specific attraction.
    Fetch from TripAdvisor API if local DB is empty.
    """
    print("Fetching detail for location_id:", pk)
    try:
        attraction = Attraction.objects.get(pk=pk)
        serializer = AttractionSerializer(attraction)
        return Response(serializer.data)
    except Attraction.DoesNotExist:
        # Fallback to TripAdvisor
        service = TripAdvisorService()
        attraction = service.sync_single_attraction(location_id=pk)
        if not attraction:
            return Response({"error": "Attraction not found"}, status=404)

        # serializer = AttractionSerializer(attraction)
        attraction_data = AttractionSerializer(attraction).data
        # return Response(serializer.data)
    # Fetch nearby attractions using TripAdvisor API
    latitude = attraction_data.get("latitude")
    longitude = attraction_data.get("longitude")
    category = attraction_data.get("category")
    category = tripadvisor_category(category)
    print("Category for nearby", category)

    nearby_results = []
    if latitude and longitude:
        try:
            nearby_results = service.search_nearby(
                latitude=float(latitude),
                longitude=float(longitude),
                category=category,
                radius=10  # default radius in km
            )
        except Exception as e:
            print("Error fetching nearby attractions:", e)

    # Include nearby attractions in response
    attraction_data["nearby_attractions"] = nearby_results

    return Response(attraction_data)

@api_view(['GET'])
def attractions_popular(request):
    country = request.GET.get('country')
    print("Country filter:", country)
    limit = int(request.GET.get('limit', 10))

    
    # If local DB is empty, fetch from TripAdvisor
    local_qs = Attraction.objects.filter(country=country)
    if not local_qs.exists():
        service = TripAdvisorService()
        # You can define a default query or country
        query = country if country else 'World'
        results = service.search_location(query=query)
        
        for result in results:
            location_id = result.get('location_id')
            details = service.get_location_details(location_id)
            if details:
                # Extract coordinates safely
                latitude = details.get('latitude') or 0.0
                longitude = details.get('longitude') or 0.0

                Attraction.objects.update_or_create(
                    tripadvisor_id=location_id,
                    defaults={
                        'name': details.get('name', ''),
                        'description': details.get('description', ''),
                        'city': result.get('address_obj', {}).get('city', ''),
                        'country': result.get('address_obj', {}).get('country', ''),
                        'latitude': latitude,
                        'longitude': longitude,
                        'rating': details.get('rating', 0),
                        'num_reviews': details.get('num_reviews', 0),
                        'photo_count': details.get('photo_count', 0),
                        'category': details.get('category', ''),
                        'website': details.get('website', ''),
                        'phone': details.get('phone', ''),
                        'photo_url': details.get('rating_image_url', ''),
                        # add other fields
                    }
                )


    # Now fetch popular attractions from local DB
    queryset = Attraction.objects.all()
    if country:
        queryset = queryset.filter(country=country)
    
    queryset = queryset.order_by('-likes_count', '-rating')[:limit]
    serializer = AttractionListSerializer(queryset, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def attraction_like(request, pk):
    try:
        attraction = Attraction.objects.get(pk=pk)
    except Attraction.DoesNotExist:
        return Response({"error": "Attraction not found"}, status=404)

    attraction.likes_count += 1
    attraction.save()
    serializer = AttractionSerializer(attraction)
    return Response(serializer.data)

@api_view(['GET'])
def attraction_similar(request, pk):
    try:
        attraction = Attraction.objects.get(pk=pk)
    except Attraction.DoesNotExist:
        return Response({"error": "Attraction not found"}, status=404)

    similar = Attraction.objects.filter(
        city=attraction.city,
        category=attraction.category
    ).exclude(id=attraction.id)[:5]

    serializer = AttractionListSerializer(similar, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def sync_from_tripadvisor(request):
    service = TripAdvisorService()
    query = request.data.get('query')
    # print("Sync query:", query)
    category = request.data.get('category')
    print("Sync query {} category: {}", query, category)

    results = service.search_location(query, category)
    synced_count = 0

    # Valid category list based on Attraction model
    valid_categories = [c[0] for c in Attraction.CATEGORY_CHOICES]

    for result in results:
        location_id = result.get('location_id')
        name = result.get('name')

        # Get TripAdvisor category if available
        category_info = result.get('category', {})
        if isinstance(category_info, dict):
            category_name = category_info.get('name', '').lower()
        else:
            category_name = None

        # ⚠️ Skip invalid or empty categories
        # if not category_name or category_name not in valid_categories:
        #     print(f"Skipping '{name}' (invalid category: {category_name})")
        #     continue

        print("Syncing location ID:", location_id)
        details = service.get_location_details(location_id)

        if not details:
            print(f"⚠️ No details found for ID {location_id}")
            continue

        # Make sure required fields are populated
        defaults = {
            'name': details.get('name', ''),
            'description': details.get('description', ''),
            'category': details.get('category', 'unknown'),
            'country': details.get('address_obj', {}).get('country', ''),
            'city': details.get('address_obj', {}).get('city', ''),
            'latitude': details.get('latitude', 0.0),
            'longitude': details.get('longitude', 0.0),
            'rating': details.get('rating', 0),
            'num_reviews': details.get('num_reviews', 0),
            'photo_count': details.get('photo_count', 0),
            'category': details.get('category', ''),
            'website': details.get('website', ''),
            'phone': details.get('phone', ''),
            'photo_url': details.get('rating_image_url', ''),
        }
        try:
            Attraction.objects.update_or_create(
                tripadvisor_id=location_id,
                defaults=defaults
            )
            synced_count += 1
        except Exception as e:
            # Log and skip errors
            print(f"Skipping attraction {location_id}: {e}")

    return Response({'synced': synced_count})

def search_tripadvisor(request):
    query = request.GET.get("q")
    print("Search query:", query)
    headers = {
        "accept": "application/json",
    }
    params = {
        "searchQuery": query,
        "language": "en",
        "key": settings.TRIPADVISOR_API_KEY
    }

    r = requests.get("https://api.content.tripadvisor.com/api/v1/location/search", headers=headers, params=params)
    return JsonResponse(r.json(), safe=False)

class AttractionViewSet(viewsets.ModelViewSet):
    queryset = Attraction.objects.all()
    serializer_class = AttractionSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'country', 'city', 'price_level']
    search_fields = ['name', 'description', 'city', 'address']
    ordering_fields = ['rating', 'likes_count', 'num_reviews', 'price_level']
    ordering = ['-likes_count']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return AttractionListSerializer
        return AttractionSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by profile type
        profile_type = self.request.query_params.get('profile_type')
        if profile_type:
            # Customize queryset based on profile type
            if profile_type == 'local':
                queryset = queryset.exclude(category='hotel')
            elif profile_type == 'professional':
                queryset = queryset.filter(
                    Q(category='restaurant') | Q(category='hotel')
                )
        
        # Filter by minimum reviews
        min_reviews = self.request.query_params.get('min_reviews')
        if min_reviews:
            queryset = queryset.filter(num_reviews__gte=int(min_reviews))
        
        # Filter by minimum photos
        min_photos = self.request.query_params.get('min_photos')
        if min_photos:
            queryset = queryset.filter(photo_count__gte=int(min_photos))
        
        # Filter by radius from location
        lat = self.request.query_params.get('latitude')
        lng = self.request.query_params.get('longitude')
        radius = self.request.query_params.get('radius', 10)  # km
        
        if lat and lng:
            queryset = self.filter_by_radius(queryset, float(lat), float(lng), float(radius))
        
        return queryset
    
    def filter_by_radius(self, queryset, lat, lng, radius):
        """Filter attractions within radius using Haversine formula"""
        def haversine(lon1, lat1, lon2, lat2):
            lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
            dlon = lon2 - lon1
            dlat = lat2 - lat1
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * asin(sqrt(a))
            km = 6371 * c
            return km
        
        filtered_ids = []
        for attraction in queryset:
            distance = haversine(
                float(lng), float(lat),
                float(attraction.longitude), float(attraction.latitude)
            )
            if distance <= radius:
                filtered_ids.append(attraction.id)
        
        return queryset.filter(id__in=filtered_ids)
    
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """Get most popular attractions by country"""
        country = request.query_params.get('country')
        limit = int(request.query_params.get('limit', 10))
        
        queryset = self.get_queryset()
        if country:
            queryset = queryset.filter(country=country)
        
        queryset = queryset.order_by('-likes_count', '-rating')[:limit]
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        """Increment likes for an attraction"""
        attraction = self.get_object()
        attraction.likes_count += 1
        attraction.save()
        serializer = self.get_serializer(attraction)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def similar(self, request, pk=None):
        """Get similar attractions in the same neighborhood"""
        attraction = self.get_object()
        similar = Attraction.objects.filter(
            city=attraction.city,
            category=attraction.category
        ).exclude(id=attraction.id)[:5]
        
        serializer = AttractionListSerializer(similar, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def sync_from_tripadvisor(self, request):
        """Sync attractions from TripAdvisor API"""
        service = TripAdvisorService()
        query = request.data.get('query')
        category = request.data.get('category')
        
        results = service.search_location(query, category)
        
        synced_count = 0
        for result in results:
            location_id = result.get('location_id')
            details = service.get_location_details(location_id)
            
            if details:
                # Map TripAdvisor data to your model
                # This is a simplified version
                Attraction.objects.update_or_create(
                    tripadvisor_id=location_id,
                    defaults={
                        'name': details.get('name', ''),
                        'description': details.get('description', ''),
                        # Add more fields...
                    }
                )
                synced_count += 1
        
        return Response({'synced': synced_count})