'use client';
import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api'
import type { Attraction } from '@/types/attractions';
import type { SearchFilters } from '@/types/search';
// import api from '@/api/attractions';

export const useSearchAttractions = (country: string, capital: string, profile_type: string) => {
  // return useQuery({
  //   queryKey: ['searchAttractions', filters],
  //   queryFn: async (): Promise<Attraction[]> => {
  //     const params: Record<string, any> = { ...filters };
      
  //     // Convert openNow en format attendu par l'API
  //     if (filters.openNow !== undefined) {
  //       params.open_now = filters.openNow ? 1 : 0;
  //     }

  //     const res = await api.get('/api/attractions_v1/search/', { params });
  //     return res.data;
  //   },
  //   // keepPreviousData: true,
  //   staleTime: 1000 * 60 * 5,
  // });
  return useQuery({
    queryKey: ['popularAttractionsByTAR', country, capital, profile_type],
    queryFn: async (): Promise<Attraction[]> => {
        const res = await api.get(`/api/attractions_v1/search_default/?country=${country}&capital=${capital}&profile_type=${profile_type}`)
        return res.data
    },
    // staleTime: 1000 * 60 * 5, // 5 minutes

    // retry: 1

  })
};
