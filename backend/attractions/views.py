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

VALID_CATEGORIES = ["hotel", "attraction", "restaurant", "geographic"]
VALID_ATTRACTIONS = ["hotel", "attraction", "restaurant"]

def extract_opening_hours(data):
    """Extrait proprement les horaires d'ouverture depuis la structure TripAdvisor"""
    hours = None
    try:
        hours = data.get("hours", {}).get("weekday_text", None)
    except Exception as e:
        print("Erreur extraction horaires :", e)
    return hours

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
def attractions_search_default(request):
    "Get default data for researchpage"
    country_query = request.GET.get('country')
    capital_query = request.GET.get('city')
    profile_type_query = request.GET.get('profile_type')
    print("Country query:", country_query)
    limit = int(request.GET.get('limit', 10))

     # Filters from frontend
    category_filter = request.GET.get('category', '').lower() or 'attractions'
    min_reviews = int(request.GET.get('minReviews', 0))
    min_photos = int(request.GET.get('minPhotos', 0))
    price_level_filter = request.GET.get('priceLevel', '').strip()
    radius_filter = float(request.GET.get('radius', ''))
    open_now = request.GET.get('openNow', '').lower() == 'true'
    print(f"[DEBUG] radius: {radius_filter}, min_reviews: {min_reviews}, min_photos: {min_photos}, price_level: {price_level_filter}, open_now: {open_now}")
    service = TripAdvisorService()
    locations = service.search_location(query=capital_query, country=country_query, category="geos")
    if not locations:
        print("No locations found for capital:", capital_query)
        return Response({"error": "No location found for capital"}, status=404)

    capital_data = locations[0]
    capital_id = capital_data.get('location_id')
    # print("{} - {}".format(capital_query, capital_id))

    capital_infos = service.get_location_details(capital_id)
    latitude = capital_infos.get('latitude')
    longitude = capital_infos.get('longitude')
    print("category filter ", category_filter)
    # print("Ville info \n", capital_infos.get("l"))
    # attraction populaires dans la ville
    search_results = service.search_nearby(
        latitude,
        longitude,
        radius=radius_filter if radius_filter > 0 else 10,
        category=category_filter)
    results = []
    # print(search_results)
    for result in search_results:
        print("Traitement \n")
        address_obj = result.get('address_obj', {})
        country_name = address_obj.get('country', '').strip()

        location_id = result.get('location_id')
        details = service.get_location_details(location_id)
        print("Location name: {}\n".format(result.get('name')))
        photos = service.get_location_photos(location_id)
       
        if not details:
            continue

        category = details.get('category', {})["name"].lower()
        if category not in VALID_CATEGORIES:
            continue
        if profile_type_query == 'local' and category == 'hotel':
            continue
        if profile_type_query == 'professional' and category not in ['restaurant', 'hotel']:
            continue

        # Apply frontend filters
        num_reviews = int(details.get('num_reviews') or 0)
        photo_count = int(details.get('photo_count') or 0)

        if min_reviews and num_reviews < min_reviews:
            continue
        if min_photos and photo_count < min_photos:
            continue
        if price_level_filter and price_level_filter != details.get('price_level', ''):
            print("price_level_filter {} category {}".format(price_level_filter, details.get('price_level', '')))
            continue
        # if open_now and not details.get('hours', {}).get('open_now_text', '').lower().startswith('open'):
            # continue

        city = address_obj.get('city', '').strip()
        address = address_obj.get('address_string', '').strip()

        # Fallback : si l’adresse est vide, on construit une version basique
        if not address:
            parts = [part for part in [city, country_name] if part]
            address = ", ".join(parts) if parts else country_name

        # Conversion sécurisée des champs numériques
        try:
            rating = float(details.get('rating', 0) or 0)
        except (ValueError, TypeError):
            rating = 0.0
        try:
            photo_url = photos[0].get('photo_url')
        except (ValueError, TypeError):
            photo_url = ""
        try:
            num_reviews = int(details.get('num_reviews') or 0)
        except (ValueError, TypeError):
            num_reviews = 0

        try:
            photo_count = int(details.get('photo_count') or 0)
        except (ValueError, TypeError):
            photo_count = 0
        
        try:
            horaires = details.get("hours", {}).get("weekday_text", None)
        except (ValueError, TypeError):
            horaires = ""
        
        print("Horaires \n", horaires)
            
        result_data = {
            "id": location_id,
            "name": details.get('name', ''),
            "description": details.get('description', ''),
            "city": city,
            "country": country_name,
            "address": address,  # avec fallback automatique
            "latitude": float(details.get('latitude') or 0.0),
            "longitude": float(details.get('longitude') or 0.0),
            "rating": rating,
            "num_reviews": num_reviews,
            "photo_count": photo_count,
            "category": details.get('category', {})["name"],
            "website": details.get('website', ''),
            "phone": details.get('phone', ''),
            "rating_image_url": details.get('rating_image_url', ''),
            "photo": photos,
            "photo_url": photo_url,
            "price_level": details.get('price_level', ''),
            "horaires": horaires

        }
        # print("result_data {} - categorie {} ".format(result_data['name'], result_data['category']))
        results.append(result_data)

    # Tri par note décroissante
    results.sort(key=lambda x: x.get('rating', 0.0), reverse=True)
    # print(results[:1])
    # Limite du nombre de résultats
    return Response(results)

@api_view(['GET'])
def attraction_detail(request, pk):
    """
    Get detailed information about a specific attraction.
    Fetch from TripAdvisor API if local DB is empty.
    """
    print("Fetching detail for location_id:", pk)
    # try:
    #     attraction = Attraction.objects.get(pk=pk)
    #     serializer = AttractionSerializer(attraction)
    #     return Response(serializer.data)
    # except Attraction.DoesNotExist:
    #     # Fallback to TripAdvisor
    #     service = TripAdvisorService()
    #     attraction = service.sync_single_attraction(location_id=pk)
    #     if not attraction:
    #         return Response({"error": "Attraction not found"}, status=404)

    #     # serializer = AttractionSerializer(attraction)
    #     attraction_data = AttractionSerializer(attraction).data
    service = TripAdvisorService()
    details = service.get_location_details(pk)
    # print("Location name: {}\n".format(result.get('name')))
    if not details:
        return Response({"error": "Attraction not found"}, status=404)
    photos = service.get_location_photos(pk) 
    # photo_url = photos[0].get('photo_url')
    try:
            photo_url = photos[0].get('photo_url')
    except (ValueError, TypeError):
            photo_url = ""
    print("photo url\n ",photo_url)
    print("photos \n ",photos)
     # Extract category safely
    category_info = details.get("category") or {}
    category_name = category_info.get("name", "").strip() or ""
    attraction_data = {
            "tripadvisor_id": details.get("location_id"),
            "name": details.get("name"),
            "description": details.get("description") or "",
            "address": details.get("address_obj", {}).get("address_string", ""),
            "city": details.get("address_obj", {}).get("city", ""),
            "country": details.get("address_obj", {}).get("country", ""),
            "latitude": details.get("latitude") or 0.0,
            "longitude": details.get("longitude") or 0.0,
            "phone": details.get("phone") or "",
            "website": details.get("website") or "",
            "email": details.get("email") or "",
            "rating": float(details.get("rating") or 0),
            "num_reviews": int(details.get("num_reviews") or 0),
            "photo_url": photo_url,
            "price_level": details.get('price_level', ''),
            "photos": photos,
            "photo_count": int(details.get("photo_count") or 0),
            "category": category_name,
            "opening_hours": details.get("hours") or {},
            "awards": details.get("awards") or [],
            "cuisine_types": details.get("cuisine") or [],
            "hotel_style": details.get("hotel_style") or [],
            "hotel_class": details.get("hotel_class") or None,
            "nearby_attractions": []
        }

    # attraction = service.sync_single_attraction(location_id=pk)
    # if not attraction:
    #     return Response({"error": "Attraction not found"}, status=404)

    # serializer = AttractionSerializer(attraction)
    # attraction_data = AttractionSerializer(attraction).data
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
    country_query = request.GET.get('country')
    print("Country query:", country_query)
    limit = int(request.GET.get('limit', 10))

    service = TripAdvisorService()
    query = country_query if country_query else 'World'

    # Recherche des locations via TripAdvisor
    search_results = service.search_location(query=query, country=country_query)
    # search_results = service.search_locations_by_country(country_name=query, limit=limit)
    # print("result ", search_results)
    results = []

    for result in search_results:
        address_obj = result.get('address_obj', {})
        country_name = address_obj.get('country', '').strip()

        # Filtrer uniquement les résultats correspondant au pays demandé
        # if not country_name or (country_query and country_name.lower() != country_query.lower()):
        #     continue

        

        location_id = result.get('location_id')
        details = service.get_location_details(location_id)
        print("Location name: {}\n".format(result.get('name')))
        photos = service.get_location_photos(location_id)
        photo_url = photos[0].get('photo_url')

        if not details:
            # print(" r ",result.get('category'))
            continue

        city = address_obj.get('city', '').strip()
        address = address_obj.get('address_string', '').strip()

        # Fallback : si l’adresse est vide, on construit une version basique
        if not address:
            parts = [part for part in [city, country_name] if part]
            address = ", ".join(parts) if parts else country_name

        # Conversion sécurisée des champs numériques
        try:
            rating = float(details.get('rating', 0) or 0)
        except (ValueError, TypeError):
            rating = 0.0

        try:
            num_reviews = int(details.get('num_reviews') or 0)
        except (ValueError, TypeError):
            num_reviews = 0

        try:
            photo_count = int(details.get('photo_count') or 0)
        except (ValueError, TypeError):
            photo_count = 0
        
        try:
            horaires = details.get("hours", {}).get("weekday_text", None)
        except (ValueError, TypeError):
            horaires = ""
        
        print("Horaires \n", horaires)
            
        result_data = {
            "id": location_id,
            "name": details.get('name', ''),
            "description": details.get('description', ''),
            "city": city,
            "country": country_name,
            "address": address,  # avec fallback automatique
            "latitude": float(details.get('latitude') or 0.0),
            "longitude": float(details.get('longitude') or 0.0),
            "rating": rating,
            "num_reviews": num_reviews,
            "photo_count": photo_count,
            "category": details.get('category', {})["name"],
            "website": details.get('website', ''),
            "phone": details.get('phone', ''),
            "rating_image_url": details.get('rating_image_url', ''),
            "photo": photos,
            "photo_url": photo_url,
            "price_level": details.get('price_level', ''),
            "horaires": horaires

        }
        # print("result_data {} - categorie {} ".format(result_data['name'], result_data['category']))
        if result_data['category'] in VALID_ATTRACTIONS:
            results.append(result_data)

    # Tri par note décroissante
    results.sort(key=lambda x: x.get('rating', 0.0), reverse=True)
    # print(results[:5])
    # Limite du nombre de résultats
    return Response(results[:limit])


    # country = request.GET.get('country')
    # print("Country filter:", country)
    # limit = int(request.GET.get('limit', 10))

    
    # # If local DB is empty, fetch from TripAdvisor
    # local_qs = Attraction.objects.filter(country=country)
    # if not local_qs.exists():
    #     service = TripAdvisorService()
    #     # You can define a default query or country
    #     query = country if country else 'World'
    #     results = service.search_location(query=query)
        
    #     for result in results:
    #         location_id = result.get('location_id')
    #         details = service.get_location_details(location_id)
    #         if not details:
    #             continue

    #         address_obj = result.get('address_obj', {})
    #         city = address_obj.get('city') or ''
    #         country_name = address_obj.get('country') or country or ''

    #         latitude = details.get('latitude') or 0.0
    #         longitude = details.get('longitude') or 0.0

    #         Attraction.objects.update_or_create(
    #             tripadvisor_id=location_id,
    #             defaults={
    #                 'name': details.get('name', ''),
    #                 'description': details.get('description', ''),
    #                 'city': city,
    #                 'country': country_name,
    #                 'latitude': latitude,
    #                 'longitude': longitude,
    #                 'rating': details.get('rating', 0),
    #                 'num_reviews': details.get('num_reviews', 0),
    #                 'photo_count': details.get('photo_count', 0),
    #                 'category': details.get('category', ''),
    #                 'website': details.get('website', ''),
    #                 'phone': details.get('phone', ''),
    #                 'photo_url': details.get('rating_image_url', ''),
    #             }
    #         )
    # for a in Attraction.objects.all():
    #     print(a.name, a.city, a.country)
    # # Now fetch popular attractions from local DB
    # queryset = Attraction.objects.all()
    # if country:
    #     queryset = queryset.filter(country=country)
    
    # queryset = queryset.order_by('-likes_count', '-rating')[:limit]
    # serializer = AttractionListSerializer(queryset, many=True)
    # return Response(serializer.data)

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