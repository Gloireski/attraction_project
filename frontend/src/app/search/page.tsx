'use client';
import { useEffect, useState } from 'react';
import { useUserSession } from '@/hooks/useUserSession';
import { useSearchAttractions } from '@/hooks/useSearchAttractions';
import { attractionsApi } from '@/api/attractions';
import { useQuery, keepPreviousData } from '@tanstack/react-query';
import AttractionsCarousel from '@/components/AttractionsCarousel';
import dynamic from 'next/dynamic';
const AttractionsMap = dynamic(() => import('@/components/AttractionsMap'), { ssr: false });
import FiltersPanel from '@/components/FiltersPanel';
import type { SearchFilters } from '@/types/search';

export default function SearchPage() {
  const { data: userSession } = useUserSession();

  console.log("user: ", userSession)

  const defaultCity = 'Paris';
  const profile_type = userSession?.profile_type || 'local'
  const city = userSession?.capital || defaultCity
  const country = userSession?.country || 'France'
  
  const [filters, setFilters] = useState<SearchFilters>({
    country,
    city,
    category: '',
    minReviews: 0,
    minPhotos: 0,
    priceLevel: '',
    radius: 20,
    openNow: false,
  });

  const { data: attractions, isLoading, isError, refetch } = useQuery({
    queryKey: ['attractions_search', country, city, profile_type, filters],
    queryFn: () => 
      attractionsApi.getPopularByTypeAndRegion(country, profile_type, filters),

    // retry: 1,
    // staleTime: 1000 * 60 * 5
    placeholderData: keepPreviousData
  });

  // 👇 Refetch automatically when filters change
  useEffect(() => {
    refetch();
  }, [filters, refetch]);

  // const { data: attractions, isLoading } = useSearchAttractions(country, capital, profile_type,);
  console.log('reserch result: ', attractions)
  return (
    <div className="px-6 py-10">
      <h1 className="text-3xl font-bold mb-6">Recherche d’attractions</h1>
      <FiltersPanel filters={filters} onChange={setFilters} />
      {isLoading ? (
        <p>Chargement...</p>
      ) : (
        <>
          <AttractionsCarousel attractions={attractions || []} />
          <AttractionsMap attractions={attractions || []} />
        </>
      )}

      {isError && (
        <p className='text-2xl text-red-600 font-medium'>Oups something went wrong</p>
      )}
    </div>
  );
}
