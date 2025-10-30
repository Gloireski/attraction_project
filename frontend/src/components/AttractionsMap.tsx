'use client';

import { motion, useMotionValue, useTransform } from 'framer-motion';
import Image from 'next/image';
import type { Attraction } from '@/types/attractions';
import { useRef } from 'react';

type Props = {
  attraction: Attraction;
  onSelect?: (id: string | number) => void;
};

export default function AttractionCard({ attraction, onSelect }: Props) {
  const cardRef = useRef<HTMLDivElement>(null);
  const x = useMotionValue(0);
  const y = useMotionValue(0);

  // Rotation en fonction de la position de la souris
  const rotateX = useTransform(y, [-100, 100], [15, -15]);
  const rotateY = useTransform(x, [-100, 100], [-15, 15]);

  const handleMouseMove = (e: React.MouseEvent) => {
    const rect = cardRef.current?.getBoundingClientRect();
    if (!rect) return;
    const offsetX = e.clientX - rect.left - rect.width / 2;
    const offsetY = e.clientY - rect.top - rect.height / 2;
    x.set(offsetX);
    y.set(offsetY);
  };

  const handleMouseLeave = () => {
    x.set(0);
    y.set(0);
  };

  return (
    <motion.div
      ref={cardRef}
      className="bg-white shadow-md hover:shadow-2xl transition-all rounded-2xl overflow-hidden border border-gray-100 cursor-pointer transform-gpu"
      style={{ rotateX, rotateY }}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      onClick={() => onSelect?.(attraction.id)}
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.97 }}
    >
      {/* Image */}
      <div className="relative h-44 w-full">
        <Image
          src={attraction?.photo_url || '/placeholder.jpg'}
          alt={attraction?.name}
          fill
          className="object-cover transition-transform duration-500 hover:scale-110"
        />
        <div className="absolute top-2 right-2 bg-white/80 backdrop-blur-sm text-sm font-medium px-2 py-1 rounded-lg">
          ⭐ {attraction?.score || 'N/A'}
        </div>
      </div>

      {/* Content */}
      <div className="p-4 flex flex-col justify-between h-40">
        <div>
          <h3 className="text-lg font-semibold text-gray-800 mb-1 truncate">
            {attraction?.name}
          </h3>
          <p className="text-gray-500 text-sm line-clamp-2">
            {attraction?.address || 'Adresse inconnue'}
          </p>
        </div>

        <div className="mt-3 flex justify-between items-center">
          <span className="text-sm font-medium text-primary">
            {attraction?.likes ?? 0} ❤️
          </span>
          <motion.button
            className="text-sm font-medium text-white bg-primary px-3 py-1 rounded-lg hover:bg-blue-700 transition"
            onClick={(e) => {
              e.stopPropagation();
              onSelect?.(attraction.id);
            }}
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
          >
            Voir plus
          </motion.button>
        </div>
      </div>
    </motion.div>
  );
}
