// routes/attraction.tsx
import { useParams } from "react-router";
import { useQuery } from "@tanstack/react-query";
import api from "../services/api";

export const AttractionPage = () => {
  const { id } = useParams<{ id: string }>();

  const { data, isLoading, error } = useQuery({
    queryKey: ["attraction", id],
    queryFn: async () => {
      const res = await api.get(`/api/attractions/${id}`);
      return res.data;
    },
    enabled: !!id, // only fetch if id exists
  });

  if (isLoading) return <p>Loading attraction...</p>;
  if (error) return <p>Error loading attraction</p>;

  return (
    <div className="p-4">
      <h1 className="text-3xl font-bold">{data.name}</h1>
      <p className="text-gray-700 mt-2">{data.description}</p>
      <p className="text-gray-500 mt-1">Category: {data.category}</p>
      <p className="text-gray-500">Price Level: {data.price_level || "N/A"}</p>
    </div>
  );
};

export const loader = async () => null;
