// src/hooks/useSearchAttractions.ts
import { useQuery } from '@tanstack/react-query';
import { attractionsApi } from '@/api/attractions';
import type { Attraction } from '@/types/attractions';

export interface AttractionFilters {
  country: string;
  city?: string;
  category?: string;
  minReviews?: number;
  minPhotos?: number;
  priceLevel?: number;
  radiusKm?: number;
  period?: string; // période d'ouverture, ex: "morning", "afternoon"
}

export const useSearchAttractions = (filters: AttractionFilters) => {
  return useQuery<Attraction[], Error>({
    queryKey: ['searchAttractions', filters],
    queryFn: async () => {
      let data = await attractionsApi.getPopular(filters.country);

      // filtrage côté frontend si nécessaire
      if (filters.city) {
        data = data.filter(
          (a) => a.city.toLowerCase() === filters.city!.toLowerCase()
        );
      }
      if (filters.category) {
        data = data.filter(
          (a) => a.category?.toLowerCase() === filters.category!.toLowerCase()
        );
      }
      if (filters.minReviews) {
        data = data.filter((a) => a.num_reviews >= filters.minReviews!);
      }
      if (filters.minPhotos) {
        data = data.filter((a) => a.photo_count >= filters.minPhotos!);
      }
      if (filters.priceLevel) {
        data = data.filter((a) => a.price_level === filters.priceLevel);
      }
      // TODO: filtrage par radius et période si coordonnées disponibles

      return data;
    },
    staleTime: 1000 * 60 * 5,
  });
};
