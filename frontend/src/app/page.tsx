'use client'

import { useQuery } from '@tanstack/react-query';
import { attractionsApi } from '@/api/attractions';
import type { Attraction } from '@/types/attractions'

export default function Home() {
  const { data: popularAttractions, isLoading } = useQuery<Attraction[]>({
    queryKey: ['popularAttractions'],
    queryFn: () => attractionsApi.getPopular('Morocco'),
  });

  if (isLoading) return <div>Loading...</div>;

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-4">Popular Attractions</h1>
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
        {popularAttractions?.map((attraction) => (
          <div
            key={attraction.id}
            className="border rounded-lg overflow-hidden shadow hover:shadow-lg transition"
          >
            {attraction.photo_url && (
              <img
                src={attraction.photo_url}
                alt={attraction.name}
                className="w-full h-48 object-cover"
              />
            )}
            <div className="p-4">
              <h2 className="text-xl font-semibold">{attraction.name}</h2>
              <p className="text-gray-500">Rating: {attraction.rating} ⭐</p>
              <p className="text-gray-400">
                {attraction.city}, {attraction.country}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
