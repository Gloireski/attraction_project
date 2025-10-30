import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet'
import { Icon } from 'leaflet'
import 'leaflet/dist/leaflet.css'
import type { Attraction } from '../../api/types/attraction'

// Fix Leaflet default icon issue
import icon from 'leaflet/dist/images/marker-icon.png'
import iconShadow from 'leaflet/dist/images/marker-shadow.png'

const DefaultIcon = new Icon({
  iconUrl: icon,
  shadowUrl: iconShadow,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
})

interface AttractionMapProps {
  attractions: Attraction[]
  center?: [number, number]
  zoom?: number
  height?: string
}

function MapUpdater({ center }: { center: [number, number] }) {
  const map = useMap()
  map.setView(center, map.getZoom())
  return null
}

export default function AttractionMap({
  attractions,
  center = [48.8566, 2.3522], // Default: Paris
  zoom = 13,
  height = '500px',
}: AttractionMapProps) {
  return (
    <MapContainer
      center={center}
      zoom={zoom}
      style={{ height: height }}
    >
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
      />
      {center && <MapUpdater center={center} />}
      {attractions.map((attraction) => (
        <Marker
          key={attraction.id}
          position={[attraction.latitude, attraction.longitude]}
          icon={DefaultIcon}
        >
          <Popup>{attraction.name}</Popup>
        </Marker>
      ))}
    </MapContainer>
  )
}