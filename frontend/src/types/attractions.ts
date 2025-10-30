export type Attraction = {
  id: number;
  tripadvisor_id: string;
  name: string;
  description?: string;
  city: string;
  country: string;
  latitude: number;
  longitude: number;
  rating: number;
  num_reviews: number;
  price_level?: number;
  category: string;
  photo_url?: string;
  likes?: number
  score?: number
  address?: string
};
