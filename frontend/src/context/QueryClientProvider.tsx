"use client"

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ReactNode, useState } from "react";

/**
 * Interface définissant les propriétés du composant ReactQueryProvider
 * @interface Props
 */
interface Props {
  children: ReactNode;  // Composants enfants à envelopper
}

/**
 * Composant fournisseur React Query pour l'application
 * Crée une instance unique de QueryClient et la fournit aux composants enfants
 * 
 * @param {Props} props - Propriétés du composant
 * @returns {JSX.Element} - Composant QueryClientProvider configuré
 */
export default function ReactQueryProvider({ children }: Props) {
  // Création d'une instance QueryClient unique qui persiste entre les rendus
  const [queryClient] = useState(() => new QueryClient({
    defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      retry: 1,
    },
  },
  }));

  // Fourniture du queryClient aux composants enfants
  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
}
