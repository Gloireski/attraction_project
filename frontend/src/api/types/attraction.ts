export interface Attraction {
  id: number
  name: string
  description: string
  location: string
  address: string
  latitude: number
  longitude: number
  image_url: string
  rating: number
  category: string
  created_at: string
  updated_at: string
}

export interface AttractionResponse {
  count: number
  next: string | null
  previous: string | null
  results: Attraction[]
}

export interface MapLocation {
  lat: number
  lng: number
}