'use client';

import { useSearchParams } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import { attractionsApi } from '@/api/attractions';
import AttractionsCarousel from '@/components/AttractionsCarousel';
import AttractionsMap from '@/components/AttractionsMap';
import { useSelectedAttractions } from '@/context/SelectedAttractionsContext';

export default function HomePage() {
  const { selectedAttractions, clearAttractions } = useSelectedAttractions();
  const searchParams = useSearchParams();
  const country = searchParams.get('country') || 'Morocco';

  const { data, isLoading } = useQuery({
    queryKey: ['popularAttractions', country],
    queryFn: () => attractionsApi.getPopular(country),
  });

  return (
    <div className="px-6 py-10">
      <h1 className="text-3xl font-bold text-primary mb-6">
        Les attractions populaires au {country}
      </h1>

      {isLoading ? (
        <p>Chargement...</p>
      ) : (
        <>
          <AttractionsCarousel 
            attractions={data || []} 
          />
          <AttractionsMap 
            attractions={data || []} 
            onSelect={(id) => console.log('Attraction sélectionnée:', id)}
           />
        </>
      )}
      {selectedAttractions.length > 0 && (
        <div className="mt-10">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-semibold text-gray-800">Mes sélections</h2>
            <button
              onClick={clearAttractions}
              className="text-sm font-bold text-red-600 hover:underline"
            >
              Vider la liste
            </button>
          </div>
          <AttractionsCarousel attractions={selectedAttractions} />
        </div>
      )}
    </div>
  );
}
