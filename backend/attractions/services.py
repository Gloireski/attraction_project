import requests
from config import settings
from typing import Dict, List, Optional
import logging
from .models import Attraction
import os
from dotenv import load_dotenv

# Charger le fichier .env
load_dotenv()

logger = logging.getLogger(__name__)

class TripAdvisorService:
    BASE_URL = settings.TRIPADVISOR_API_URL
    API_KEY = os.getenv("TRIPADVISOR_API_KEY")
    
    def __init__(self):
        self.headers = {
            'accept': 'application/json',
            # 'Referer': 'http://localhost:5173'  # Required by TripAdvisor
        }
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make request to TripAdvisor API"""
        if not params:
            params = {}
        params['key'] = self.API_KEY
        
        url = f"{self.BASE_URL}/{endpoint}"
        # print("url:", url)
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"TripAdvisor API Error: {e}")
            return None
    
    def search_location(self, query: str, category: str = None) -> List[Dict]:
        """Search for locations"""
        params = {
            'searchQuery': query,
            'language': 'fr'
        }
        if category:
            params['category'] = category
        
        data = self._make_request('location/search', params)
        print("Search Location Data:", data)
        return data.get('data', []) if data else []
    
    def sync_single_attraction(self, location_id):
        details = self.get_location_details(location_id)
        if not details:
            return None
        # Extract category safely
        category_info = details.get("category") or {}
        category_name = category_info.get("name", "").strip() or ""
        # Map only fields that exist in Attraction model
        defaults = {
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
            "photo_url": details.get("rating_image_url") or "",
            "photo_count": int(details.get("photo_count") or 0),
            "category": category_name,
            "opening_hours": details.get("hours") or {},
            "awards": details.get("awards") or [],
            "cuisine_types": details.get("cuisine") or [],
            "hotel_style": details.get("hotel_style") or [],
            "hotel_class": details.get("hotel_class") or None,
        }

        attraction, _ = Attraction.objects.update_or_create(
            tripadvisor_id=location_id,
            defaults=defaults
        )
        return attraction

    
    def get_location_details(self, location_id: str) -> Optional[Dict]:
        """Get detailed information about a location"""
        # data = self._make_request(f'location/{location_id}/details', {
        #     'language': 'fr',
        #     'currency': 'EUR'
        # })
        # return data
        return self._make_request(
            f"location/{location_id}/details",
            {"language": "fr", "currency": "EUR"}
        )
    
    def get_location_photos(self, location_id: str, limit: int = 10) -> List[Dict]:
        """Get photos for a location"""
        data = self._make_request(f'location/{location_id}/photos', {
            'language': 'fr',
            'limit': limit
        })
        return data.get('data', []) if data else []
    
    def get_location_reviews(self, location_id: str, limit: int = 10) -> List[Dict]:
        """Get reviews for a location"""
        data = self._make_request(f'location/{location_id}/reviews', {
            'language': 'fr',
            'limit': limit
        })
        return data.get('data', []) if data else []
    
    def search_nearby(self, latitude: float, longitude: float, category: str = None, radius: int = 10) -> List[Dict]:
        """Search for nearby locations"""
        params = {
            'latLong': f"{latitude},{longitude}",
            'radius': radius,
            'radiusUnit': 'km',
            'language': 'fr'
        }
        print("Searching nearby with params:", params.values())
        if category:
            params['category'] = category
        
        data = self._make_request('location/nearby_search', params)
        return data.get('data', []) if data else []