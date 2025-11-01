type Photo = {
  id: number;
  caption: string;
  photo_url?: string;
  username?: string;
}

export type SearchFilters = {
  country?: string;
  city?: string;
  category?: string;
  minReviews?: number;
  minPhotos?: number;
  priceLevel?: string;
  openNow?: boolean; // pour filtrer les attractions actuellement ouvertes
};


export type Attraction = {
  id: string; // location_id renvoyé par TripAdvisor
  name: string;
  description?: string;
  city: string;
  country: string;
  address: string; // ✅ ajouté avec fallback "city, country"
  latitude: number;
  longitude: number;
  rating: number;
  num_reviews: number;
  photo_count: number;
  category?: string; // ✅ l'API renvoie parfois un objet pour category
  website?: string;
  phone?: string;
  rating_image_url?: string;
  photo: Photo;
  likes?: number; // champ local éventuel si tu ajoutes un système de like
  score?: number; // champ calculé optionnel (si tu veux un score custom)
  price_level?: string;
  horaires?: string[]
  
};
