// context/SelectedAttractionsContext.tsx
'use client';

import { createContext, useContext, useState, ReactNode } from 'react';
import type { Attraction } from '@/types/attractions';
import { attractionsApi } from '@/api/attractions';
import { toast } from 'react-hot-toast'

type ContextType = {
  selectedAttractions: Attraction[];
  addAttraction: (a: Attraction) => void;
  removeAttraction: (id: number) => void;
  clearAttractions: () => Promise<void>;
  compilationId: number | null;
  loading: boolean;
};

const SelectedAttractionsContext = createContext<ContextType | undefined>(undefined);

export const SelectedAttractionsProvider = ({ children }: { children: ReactNode }) => {
  const [selectedAttractions, setSelectedAttractions] = useState<Attraction[]>([]);
  const [compilationId, setCompilationId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);

  const addAttraction = (a: Attraction) => {
    setSelectedAttractions(prev => [...prev, a]);
    // Optionnel: appel API pour sauvegarder côté backend
    // await attractionsApi.addToCompilation(a.id)
  };

  const removeAttraction = (id: number) => {
    setSelectedAttractions(prev => prev.filter(a => a.id !== id));
    // Optionnel: appel API pour retirer côté backend
    // await attractionsApi.removeFromCompilation(id)
  };

  const clearAttractions = () => {
    setSelectedAttractions([]);
    // Optionnel: appel API pour vider compilation
  };

  return (
    <SelectedAttractionsContext.Provider value={{ selectedAttractions, addAttraction, removeAttraction, clearAttractions }}>
      {children}
    </SelectedAttractionsContext.Provider>
  );
};

export const useSelectedAttractions = () => {
  const context = useContext(SelectedAttractionsContext);
  if (!context) throw new Error("useSelectedAttractions must be used within SelectedAttractionsProvider");
  return context;
};
