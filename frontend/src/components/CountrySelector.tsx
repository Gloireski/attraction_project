type Props = {
  value: string;
  onChange: (country: string) => void;
};

const countries = ['Maroc', 'France', 'Sénégal', 'Kenya', 'Egypte', 'Espagne'];

export default function CountrySelector({ value, onChange }: Props) {
  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="w-full border-2 border-gray-300 rounded-xl p-3 text-gray-700 focus:border-primary focus:ring-primary"
    >
      <option value="">-- Choisir un pays --</option>
      {countries.map((country) => (
        <option key={country} value={country}>
          {country}
        </option>
      ))}
    </select>
  );
}
