'use client';

import { useState } from 'react';
import { useUserSession } from '@/hooks/useUserSession';
import { useSearchAttractions } from '@/hooks/useSearchAttractions';
import AttractionsCarousel from '@/components/AttractionsCarousel';
import AttractionsMap from '@/components/AttractionsMap';
import FiltersPanel from '@/components/FiltersPanel';
import { data } from 'framer-motion/m';

export default function SearchPage() {
  const { data: userSession } = useUserSession();
  console.log(data)
  const defaultCity = userSession?.country === 'Maroc' ? 'Rabat' : 'Paris'; // exemple
  const [filters, setFilters] = useState({
    country: userSession?.country || 'Maroc',
    city: defaultCity,
    category: '',
    minReviews: 0,
    minPhotos: 0,
    priceLevel: undefined,
  });

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
