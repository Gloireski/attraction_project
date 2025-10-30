import requests
from config import settings
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class TripAdvisorService:
    BASE_URL = settings.TRIPADVISOR_API_URL
    API_KEY = settings.TRIPADVISOR_API_KEY
    
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
        if category:
            params['category'] = category
        
        data = self._make_request('location/nearby_search', params)
        return data.get('data', []) if data else []