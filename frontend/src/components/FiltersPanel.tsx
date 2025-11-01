'use client';

type Props = {
  filters: any;
  onChange: (filters: any) => void;
};

const CATEGORIES = [
  { value: 'attractions', label: 'Attractions' },
  { value: 'restaurants', label: 'Restaurants' },
  { value: 'hotels', label: 'Hotels' },
  { value: 'geos', label: 'Sites géographiques' },
];

const DAYS = [
  'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'
];

export default function FiltersPanel({ filters, onChange }: Props) {
  const toggleCategory = (category: string) => {
    const current = filters.categories || [];
    if (current.includes(category)) {
      onChange({ ...filters, categories: current.filter((c: string) => c !== category) });
    } else {
      onChange({ ...filters, categories: [...current, category] });
    }
  };

  const toggleDay = (day: string) => {
    const current = filters.days || [];
    if (current.includes(day)) {
      onChange({ ...filters, days: current.filter((d: string) => d !== day) });
    } else {
      onChange({ ...filters, days: [...current, day] });
    }
  };

  return (
    <div className="flex flex-col gap-4 mb-6">
      <div className="flex flex-wrap gap-4">
        <input
          type="text"
          placeholder="Ville"
          value={filters.city || ''}
          onChange={(e) => onChange({ ...filters, city: e.target.value })}
          className="border rounded px-2 py-1"
        />
        <input
          type="number"
          placeholder="Rayon (km)"
          value={filters.radius || ''}
          onChange={(e) => onChange({ ...filters, radius: +e.target.value })}
          className="border rounded px-2 py-1"
        />
        <input
          type="number"
          placeholder="Min reviews"
          value={filters.minReviews || 0}
          onChange={(e) => onChange({ ...filters, minReviews: +e.target.value })}
          className="border rounded px-2 py-1"
        />
        <input
          type="number"
          placeholder="Min photos"
          value={filters.minPhotos || 0}
          onChange={(e) => onChange({ ...filters, minPhotos: +e.target.value })}
          className="border rounded px-2 py-1"
        />
        <select
          value={filters.priceLevel || ''}
          onChange={(e) => onChange({ ...filters, priceLevel: e.target.value })}
          className="border rounded px-2 py-1"
        >
          <option value="">Niveau de prix</option>
          <option value="$">$</option>
          <option value="$$">$$</option>
          <option value="$$$">$$$</option>
          <option value="$$$$">$$$$</option>
        </select>
      </div>

      {/* Catégories */}
      <div className="flex gap-4 flex-wrap">
        {CATEGORIES.map((cat) => (
          <label key={cat.value} className="flex items-center gap-1">
            <input
              type="checkbox"
              checked={(filters.categories || []).includes(cat.value)}
              onChange={() => toggleCategory(cat.value)}
              className="border rounded"
            />
            {cat.label}
          </label>
        ))}
      </div>

      {/* Période d'ouverture (jours) */}
      <div className="flex gap-4 flex-wrap">
        {DAYS.map((day) => (
          <label key={day} className="flex items-center gap-1">
            <input
              type="checkbox"
              checked={(filters.days || []).includes(day)}
              onChange={() => toggleDay(day)}
              className="border rounded"
            />
            {day.slice(0, 3)}
          </label>
        ))}
      </div>
    </div>
  );
}
