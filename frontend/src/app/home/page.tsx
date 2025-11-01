'use client';

import { useSearchParams } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import { attractionsApi } from '@/api/attractions';
import AttractionsCarousel from '@/components/AttractionsCarousel';
// 🟢 Import dynamique : évite le rendu SSR pour Leaflet
import dynamic from 'next/dynamic';
const AttractionsMap = dynamic(() => import('@/components/AttractionsMap'), {
  ssr: false,
});
import { useSelectedAttractions } from '@/context/SelectedAttractionsContext';
import { useUserSession } from '@/hooks/useUserSession';

export default function HomePage() {
  const { selectedAttractions, clearAttractions } = useSelectedAttractions();
  // const { data: user, isError } = useUserSession()
  const searchParams = useSearchParams();
  // const country = searchParams.get('country') || 'Morocco';

  const { data: user, isError, isLoading: sessionLoading } = useUserSession();

  //Si aucune session n'existe, on en crée une par défaut
  // useEffect(() => {
  //   if (isError) {
  //     console.log('Aucune session trouvée, création en cours...');
  //     createSession.mutate({ profile_type: 'guest', country: 'Kenya' });
  //   }
  // }, [isError, createSession]);

  // Déterminer le pays à partir de la session ou du paramètre URL
  const country =
    searchParams.get('country') ||
    user?.country

  const { data, isLoading } = useQuery({
    queryKey: ['popularAttractions', country],
    queryFn: () => attractionsApi.getPopular(country),
  });

  return (
    <div className="px-6 py-10">
      <h1 className="text-3xl font-bold text-primary mb-6">
        Les attractions populaires: {country}
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
