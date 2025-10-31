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
  photo_url?: string;
  likes?: number; // champ local éventuel si tu ajoutes un système de like
  score?: number; // champ calculé optionnel (si tu veux un score custom)
  price_level?: string
};
