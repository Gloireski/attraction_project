'use client';

import { useParams } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import api from '@/api/attractions';
import Image from 'next/image';
import Link from 'next/link';
import type { Attraction } from '@/types/attractions';

export default function AttractionPage() {
  const { id } = useParams();

  console.log("attraction: ", id)

  const { data: attraction, isLoading, error } = useQuery({
    queryKey: ['attractionDetail', id],
    queryFn: async (): Promise<Attraction> => {
      const res = await api.get(`/api/attractions_v1/${id}/`);
      return res.data;
    },
    enabled: !!id,
  });

  if (isLoading) return <p className="p-6">Chargement...</p>;
  if (error || !attraction) return <p className="p-6 text-red-500">Erreur ou attraction introuvable</p>;

  return (
    <div className="max-w-5xl mx-auto px-6 py-10">
      {/* Titre + Note */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-6">
        <h1 className="text-4xl font-bold">{attraction.name}</h1>
        {attraction.rating && (
          <div className="text-yellow-500 text-xl font-semibold">
            ⭐ {attraction.rating} / 5 ({attraction.num_reviews} avis)
          </div>
        )}
      </div>

      {/* Image principale */}
      {attraction.photo_url && (
        <div className="relative w-full h-80 rounded-xl overflow-hidden mb-6">
          <Image
            src={attraction.photo_url }
            alt={attraction.name}
            fill
            className="object-cover"
          />
        </div>
      )}

      {/* Infos principales */}
      <div className="mb-6 space-y-2">
        <p className="text-gray-700">{attraction.description || 'Aucune description disponible.'}</p>
        <p className="text-sm text-gray-600">📍 {attraction.address}</p>
        {attraction.phone && <p className="text-sm text-gray-600">📞 {attraction.phone}</p>}
        {attraction.website && (
          <Link href={attraction.website} target="_blank" className="text-blue-500 underline text-sm">
            🌐 Site officiel
          </Link>
        )}
      </div>

      {/* Détails supplémentaires */}
      <div className="grid md:grid-cols-2 gap-4 mb-6">
        <div className="p-4 border rounded-lg">
          <h3 className="font-semibold mb-2">Informations</h3>
          <ul className="text-sm space-y-1">
            <li><strong>Pays:</strong> {attraction.country}</li>
            <li><strong>Ville:</strong> {attraction.city}</li>
            <li><strong>Catégorie:</strong> {attraction.category || 'Non spécifiée'}</li>
            <li><strong>Niveau de prix:</strong> {attraction.price_level || 'Non indiqué'}</li>
            {attraction.horaires && (
              <li>
                <strong>Horaires :</strong>
                <ul className="ml-4 list-disc text-gray-600">
                  {attraction.horaires.map((h, idx) => (
                    <li key={idx}>{h}</li>
                  ))}
                </ul>
              </li>
            )}
          </ul>
        </div>

        {/* Informations spécifiques selon type */}
        <div className="p-4 border rounded-lg">
          <h3 className="font-semibold mb-2">Détails spécifiques</h3>
          <ul className="text-sm space-y-1 text-gray-700">
            {attraction.category === 'restaurant' && attraction.cuisine && (
              <li><strong>Type de cuisine :</strong> {attraction.cuisine.join(', ')}</li>
            )}
            {attraction.category === 'hotel' && attraction.style && (
              <li><strong>Style :</strong> {attraction.style}</li>
            )}
            {attraction.category === 'attraction' && attraction.groups && (
              <li><strong>Groupes :</strong> {attraction.groups.join(', ')}</li>
            )}
          </ul>
        </div>
      </div>

      {/* Récompenses */}
      {attraction.awards && attraction.awards.length > 0 && (
        <div className="mb-6">
          <h3 className="font-semibold mb-2">🏆 Récompenses</h3>
          <ul className="list-disc ml-6 text-gray-700">
            {attraction.awards.map((a, idx) => (
              <li key={idx}>{a.display_name}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Galerie de photos secondaires */}
      {attraction.photos && attraction.photos.length > 1 && (
        <div className="mb-10">
          <h3 className="font-semibold mb-3">📸 Galerie</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {attraction.photos.slice(1, 9).map((photo, idx) => (
              <div key={idx} className="relative w-full h-40 rounded-lg overflow-hidden">
                <Image
                  src={photo.photo_url}
                  alt={photo.caption || 'Photo'}
                  fill
                  className="object-cover"
                />
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Suggestions similaires */}
      {attraction.similar && attraction.similar.length > 0 && (
        <div>
          <h3 className="font-semibold mb-3">Suggestions similaires</h3>
          <div className="grid md:grid-cols-3 gap-4">
            {attraction.similar.map((sim) => (
              <Link
                key={sim.id}
                href={`/attractions/${sim.id}`}
                className="border rounded-lg p-3 hover:bg-gray-50 transition"
              >
                <p className="font-medium">{sim.name}</p>
                <p className="text-sm text-gray-600">{sim.city}</p>
              </Link>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
