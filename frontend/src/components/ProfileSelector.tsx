type Props = {
  selected: string | null;
  onSelect: (role: string) => void;
};

const profiles = [
  { id: 'local', label: 'Local', emoji: '🏠' },
  { id: 'tourist', label: 'Touriste', emoji: '🧳' },
  { id: 'pro', label: 'Professionnel', emoji: '💼' },
];

export default function ProfileSelector({ selected, onSelect }: Props) {
  return (
    <div className="flex gap-6">
      {profiles.map((p) => (
        <button
          key={p.id}
          onClick={() => onSelect(p.id)}
          className={`px-6 py-3 border-2 rounded-xl font-medium text-lg transition ${
            selected === p.id
              ? 'border-primary text-primary bg-blue-50'
              : 'border-gray-300 hover:border-primary'
          }`}
        >
          {p.emoji} {p.label}
        </button>
      ))}
    </div>
  );
}
