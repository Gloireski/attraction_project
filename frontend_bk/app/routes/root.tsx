// routes/root.tsx
import { Outlet } from "react-router";
import { QueryClientProvider } from "@tanstack/react-query";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";
import { queryClient } from "../queryClient";

export const Root = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <div className="min-h-screen flex flex-col">
        <header className="p-4 bg-blue-600 text-white font-bold">
          Travel Explorer
        </header>
        <main className="flex-1 p-4">
          <Outlet />
        </main>
      </div>
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
};

// Root loader (required by @react-router/dev)
export const loader = async () => null;
