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

    VALID_CATEGORIES = ["hotel", "attraction", "restaurant", "geographic"]
    
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
    
    def search_locations_by_country(self, country_name: str, limit):
        """Return all TripAdvisor locations in a given country"""
        search_results = []
        page_offset = 0
        while True:
            try:
                response = self.search_location(
                    query=country_name,
                    category=None,  # None to include all categories
                    # limit=limit,       # max per page if supported
                    # offset=page_offset,
                    # language="fr"
                )
            except Exception as e:
                print(f"TripAdvisor API Error: {e}")
                break

            if not response or "data" not in response or len(response["data"]) == 0:
                break

            # Filter by country in address_obj
            filtered = [
                item for item in response["data"]
                if item.get("address_obj", {}).get("country") == country_name
                and item.get("category", {}).get("name") in self.VALID_CATEGORIES
            ]
            search_results.extend(filtered)

            # Pagination check
            if len(response["data"]) < 50:
                break
            page_offset += 50

        return search_results

    def search_location(self, query: str, category: str = None, country: str = None) -> List[Dict]:
        """Search for locations"""
        params = {
            'searchQuery': query,
            'language': 'fr'
        }
        if category:
            params['category'] = category
        if country:
            params['address'] = country
        print("params ", params)
        
        data = self._make_request('location/search', params)
        # print("Search Location Data:", data)
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
    
    def get_location_photos(self, location_id: int) -> Optional[Dict[str, str]]:
        """
        Fetch photos for a TripAdvisor location and return in a simplified format for carousel.

        Args:
            location_id (int): TripAdvisor location ID
        Returns:
            List[Dict]: List of photo dicts, each containing:
                - id
                - caption
                - photo_url (medium or original image)
                - username
        """
        params = {
            # 'locationId': location_id,
            'language': 'fr'
        }

        # print("get photos {} params {}".format(location_id, params))
        try:
            response = self._make_request(f"location/{location_id}/photos", params)
            # response.raise_for_status()
            data = response.get('data', [])

            if not data:
                return None
            photos = []

            for item in data:
                images = item.get("images", {})
                photo_url = (
                    images.get("medium", {}).get("url") or
                    images.get("original", {}).get("url") or
                    images.get("small", {}).get("url") or ""
                )

                photos.append({
                    "photo_url": photo_url,
                    "caption": item.get("caption") or "",
                    "username": item.get("user", {}).get("username") or "",
                })

            return photos
        except Exception as e:
            print(f"TripAdvisor API Error: {e}")
            return None


    def get_location_details(self, location_id: str) -> Optional[Dict]:
        """Get detailed information about a location"""
        data = self._make_request(f'location/{location_id}/details', {
            'language': 'fr',
            'currency': 'EUR'
        })
        # print("data attempt :",data)
        # print("Location id {} \n infos \n:".format(location_id, data))
        return data
        # return self._make_request(
        #     f"location/{location_id}/details",
        #     {"language": "fr", "currency": "EUR"}
        # )
    
    def get_location_reviews(self, location_id: str, limit: int = 10) -> List[Dict]:
        """Get reviews for a location"""
        data = self._make_request(f'location/{location_id}/reviews', {
            'language': 'fr',
            'limit': limit
        })
        return data.get('data', []) if data else []
    
    def search_nearby(self, latitude: float, longitude: float, address: str = None, radius: int = 10) -> List[Dict]:
        """Search for nearby locations"""
        params = {
            'latLong': f"{latitude},{longitude}",
            'radius': radius,
            'radiusUnit': 'km',
            'language': 'fr'
        }
        print("Searching nearby with params:", params.values())
        if address:
            params['address'] = address
        
        data = self._make_request('location/nearby_search', params)
        return data.get('data', []) if data else []