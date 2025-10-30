'use client';

import Image from 'next/image';
import type { Attraction } from '@/types/attractions';

type Props = {
  attraction: Attraction;
  onSelect?: (id: string | number) => void;
};

export default function AttractionCard({ attraction, onSelect }: Props) {
  return (
    <div
      className="bg-white shadow-md hover:shadow-xl transition-all rounded-2xl overflow-hidden border border-gray-100 cursor-pointer"
      onClick={() => onSelect?.(attraction.id)}
    >
      {/* Image */}
      <div className="relative h-44 w-full">
        <Image
          src={attraction.photo_url || '/placeholder.jpg'}
          alt={attraction.name}
          fill
          className="object-cover"
        />
        <div className="absolute top-2 right-2 bg-white/80 text-sm font-medium px-2 py-1 rounded-lg">
          ⭐ {attraction.score || 'N/A'}
        </div>
      </div>

      {/* Content */}
      <div className="p-4 flex flex-col justify-between h-40">
        <div>
          <h3 className="text-lg font-semibold text-gray-800 mb-1 truncate">
            {attraction.name}
          </h3>
          <p className="text-gray-500 text-sm line-clamp-2">
            {attraction.address || 'Adresse inconnue'}
          </p>
        </div>

        <div className="mt-3 flex justify-between items-center">
          <span className="text-sm font-medium text-primary">
            {attraction.likes ?? 0} ❤️
          </span>
          <button
            className="text-sm font-medium text-white bg-primary px-3 py-1 rounded-lg hover:bg-blue-700 transition"
            onClick={(e) => {
              e.stopPropagation();
              onSelect?.(attraction.id);
            }}
          >
            Voir plus
          </button>
        </div>
      </div>
    </div>
  );
}
