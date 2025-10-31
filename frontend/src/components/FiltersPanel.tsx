'use client';

type Props = {
  filters: any;
  onChange: (filters: any) => void;
};

export default function FiltersPanel({ filters, onChange }: Props) {
  return (
    <div className="flex flex-wrap gap-4 mb-6">
      <input
        type="text"
        placeholder="Ville"
        value={filters.city}
        onChange={(e) => onChange({ ...filters, city: e.target.value })}
        className="border rounded px-2 py-1"
      />
      <input
        type="number"
        placeholder="Min reviews"
        value={filters.minReviews}
        onChange={(e) => onChange({ ...filters, minReviews: +e.target.value })}
        className="border rounded px-2 py-1"
      />
      <input
        type="number"
        placeholder="Min photos"
        value={filters.minPhotos}
        onChange={(e) => onChange({ ...filters, minPhotos: +e.target.value })}
        className="border rounded px-2 py-1"
      />
      <select
        value={filters.category}
        onChange={(e) => onChange({ ...filters, category: e.target.value })}
        className="border rounded px-2 py-1"
      >
        <option value="">Toutes catégories</option>
        <option value="attractions">Attractions</option>
        <option value="restaurants">Restaurants</option>
        <option value="geos">Sites géographique</option>
      </select>
    </div>
  );
}
