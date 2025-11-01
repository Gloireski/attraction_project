'use client';
import { useState } from 'react';
import { useUserSession } from '@/hooks/useUserSession';
import { useSearchAttractions } from '@/hooks/useSearchAttractions';
import AttractionsCarousel from '@/components/AttractionsCarousel';
import dynamic from 'next/dynamic';
const AttractionsMap = dynamic(() => import('@/components/AttractionsMap'), { ssr: false });
import FiltersPanel from '@/components/FiltersPanel';
import type { SearchFilters } from '@/types/search';
import { attractionsApi } from '@/api/attractions';
import { useQuery } from '@tanstack/react-query';

export default function SearchPage() {
  const { data: userSession } = useUserSession();

  const defaultCity = 'Paris';
  const profile_type = userSession?.profile_type || 'local'
  const capital = userSession?.capital || defaultCity
  const country = userSession?.country || 'France'
  
  const [filters, setFilters] = useState<SearchFilters>({
    country: userSession?.country || 'France',
    city: userSession?.capital || defaultCity,
    category: '',
    minReviews: 0,
    minPhotos: 0,
    priceLevel: '',
    openNow: false,
  });

  // const { data, isLoading } = useQuery({
  //   queryKey: ['popularAttractionsByTAR', country, capital, profile_type, ],
  //   queryFn: () => attractionsApi.getPopularByTypeAndRegion(country, capital, profile_type),
  // });

  const { data: attractions, isLoading } = useSearchAttractions(country, capital, profile_type,);

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
    </div>
  );
}
