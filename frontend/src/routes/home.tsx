import { useLoaderData } from "react-router";
import type { LoaderFunction } from "react-router";

export const loader: LoaderFunction = async () => {
  return JSON.stringify({
    message: "Welcome to the home page"
  });
};

export default function Home() {
  const { message } = useLoaderData<{ message: string }>();
  
  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Home</h1>
      <p>{message}</p>
    </div>
  );
}