'use client';

import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import type { Attraction } from '@/types/attractions';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import { motion } from 'framer-motion';

// Fix icône par défaut Leaflet
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.3/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.3/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.3/dist/images/marker-shadow.png',
});

type Props = { attractions: Attraction[]; onSelect?: (id: string | number) => void };

export default function AttractionsMap({ attractions, onSelect }: Props) {
  if (!attractions || attractions.length === 0) return null;

  // Filtrer les attractions avec coords valides
  const validAttractions = attractions.filter(a => a.latitude && a.longitude);

  // Centrer la carte sur la première attraction
  const center: [number, number] = [
    validAttractions[0].latitude,
    validAttractions[0].longitude,
  ];

  return (
    <MapContainer center={center} zoom={6} scrollWheelZoom={true} className="my-6 h-96 w-full">
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      {validAttractions.map((a) => (
        <Marker key={a.id} position={[a.latitude, a.longitude]}>
          <Popup>
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              whileHover={{ scale: 1.05 }}
              className="p-2 w-64"
              onClick={() => onSelect?.(a.id)}
            >
              <h3 className="text-lg font-semibold">{a.name}</h3>
              <p className="text-sm text-gray-600 line-clamp-2">{a.address || a.city}</p>
              <div className="mt-1 flex justify-between items-center">
                <span className="text-sm font-medium text-primary">⭐ {a.num_reviews}</span>
                <span className="text-sm font-medium text-red-500">❤️ {a.rating ?? 0}</span>
              </div>
            </motion.div>
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  );
}
