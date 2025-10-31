import { useSelectedAttractions } from '@/context/SelectedAttractionsContext';
import { motion } from 'framer-motion';
import Image from 'next/image';
import type { Attraction } from '@/types/attractions';
import { useRef } from 'react';

type Props = { attraction: Attraction };

export default function AttractionCard({ attraction }: Props) {
  const { selectedAttractions, addAttraction, removeAttraction } = useSelectedAttractions();
  const isSelected = selectedAttractions.some((a) => a.id === attraction.id);

  const handleToggleSelect = () => {
    if (isSelected) removeAttraction(attraction.id);
    else addAttraction(attraction);
  };

  return (
    <motion.div
      className="bg-white shadow-md hover:shadow-2xl transition-all rounded-2xl overflow-hidden border border-gray-100 cursor-pointer transform-gpu"
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.97 }}
    >
      {/* Image */}
      <div className="relative h-44 w-full">
        <Image
          src={attraction?.photo.photo_url || '/placeholder.jpg'}
          alt={attraction?.name || ""}
          fill
          className="object-cover"
        />
        <div className="absolute top-2 right-2 bg-white/80 px-2 py-1 rounded-lg text-sm font-medium">
          ⭐ {attraction?.num_reviews || 'N/A'}
        </div>
      </div>

      {/* Infos */}
      <div className="p-4 flex flex-col justify-between h-40">
        <div>
          <h3 className="text-lg font-semibold mb-1 truncate">{attraction.name}</h3>
          <p className="text-gray-500 text-sm line-clamp-2">
            {attraction.address || 'Adresse inconnue'}
          </p>
        </div>

        <div className="mt-3 flex justify-between items-center">
          <span className="text-sm font-medium text-primary">
            {attraction.rating ?? 0} ❤️
          </span>
          <motion.button
            onClick={handleToggleSelect}
            className={`text-sm font-medium px-3 py-1 rounded-lg transition ${
              isSelected ? 'bg-red-500 text-white' : 'bg-primary text-white hover:bg-blue-700'
            }`}
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
          >
            {isSelected ? 'Retirer' : 'Ajouter'}
          </motion.button>
        </div>
      </div>
    </motion.div>
  );
}
