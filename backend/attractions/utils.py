# utils.py

TRIPADVISOR_CATEGORY_MAP = {
    "hotel": "hotels",
    "hotels": "hotels",
    "attraction": "attractions",
    "attractions": "attractions",
    "restaurant": "restaurants",
    "restaurants": "restaurants",
    "geo": "geos",
    "geos": "geos"
}

def tripadvisor_category(category_name: str) -> str:
    """
    Convert a local category name to TripAdvisor API category.
    Default to 'attractions' if unknown.
    """
    if not category_name:
        return "attractions"
    
    category_name = category_name.lower().strip()
    return TRIPADVISOR_CATEGORY_MAP.get(category_name, "attractions")
