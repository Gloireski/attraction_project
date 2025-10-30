'use client';

import { useSearchParams } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import { attractionsApi } from '@/api/attractions';
import AttractionsCarousel from '@/components/AttractionsCarousel';
import AttractionsMap from '@/components/AttractionsMap';

export default function HomePage() {
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
          <AttractionsCarousel attractions={data || []} />
          <AttractionsMap attractions={data || []} />
        </>
      )}
    </div>
  );
}
