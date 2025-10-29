// routes/home.tsx
import { useQuery } from "@tanstack/react-query";
import api from "../services/api";

export const Home = () => {
  const { data, isLoading, error } = useQuery({
    queryKey: ["attractions"],
    queryFn: async () => {
      const res = await api.get("/api/attractions");
      return res.data;
    },
  });

  if (isLoading) return <p>Loading attractions...</p>;
  if (error) return <p>Error loading attractions</p>;

  return (
    <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
      {data.map((attr: any) => (
        <div key={attr.id} className="card p-4 shadow rounded">
          <h3 className="font-bold text-lg">{attr.name}</h3>
          <p className="text-gray-600">{attr.category}</p>
        </div>
      ))}
    </div>
  );
};

// Optional loader if you want server-side initial data
export const loader = async () => null;
