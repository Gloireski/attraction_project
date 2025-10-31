'use client';

import { useState } from 'react';
import { useUserSession } from '@/hooks/useUserSession';
import { useSearchAttractions } from '@/hooks/useSearchAttractions';
import AttractionsCarousel from '@/components/AttractionsCarousel';
// import AttractionsMap from '@/components/AttractionsMap';
// 🟢 Import dynamique : évite le rendu SSR pour Leaflet
// import { useCountryCapital } from '@/hooks/useCountryCapital';
import dynamic from 'next/dynamic';
const AttractionsMap = dynamic(() => import('@/components/AttractionsMap'), {
  ssr: false,
});
import FiltersPanel from '@/components/FiltersPanel';

export default function SearchPage() {
  const { data: userSession } = useUserSession();
  console.log(userSession)
//   const {data} = useCountryCapital(userSession?.country)
  const defaultCity ='Paris'; // exemple
  const [filters, setFilters] = useState({
    country: userSession?.country || 'France',
    city: userSession?.capital || defaultCity,
    category: '',
    minReviews: 0,
    minPhotos: 0,
    priceLevel: undefined,
  });

  console.log("filtres ", filters)
  const { data: attractions, isLoading } = useSearchAttractions(filters);

  return (
    <div className="px-6 py-10">
      <h1 className="text-3xl font-bold mb-6">Recherche d’attractions</h1>

      {/* Panel de filtres */}
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
