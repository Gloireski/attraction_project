'use client';
import { motion } from 'framer-motion';
import { useState } from 'react';
import { useSelectedAttractions } from '@/context/SelectedAttractionsContext';
import { attractionsApi } from '@/api/attractions';
import AttractionsCarousel from '@/components/AttractionsCarousel';
import { toast } from 'react-hot-toast';
import { Loader2, Map, ArrowDownUp, Trash2 } from 'lucide-react';

export default function CompilationPage() {
  const { selectedAttractions, removeAttraction, clearAttractions, compilationId, loading } = useSelectedAttractions();
  const [sorting, setSorting] = useState(false);
  const [optimizing, setOptimizing] = useState(false);
  const [budgetTotal, setBudgetTotal] = useState<number | null>(null);

  if (loading) return <p className="text-center py-10">Chargement de ta compilation...</p>;

  const handleSortByBudget = async () => {
    if (!compilationId) return;
    setSorting(true);
    try {
      const sorted = await attractionsApi.sortByBudget(compilationId);
      toast.success('Compilation triée par budget 💶');
      setBudgetTotal(sorted.total_budget);
    } catch (err) {
      toast.error('Erreur tri par budget');
      console.error(err);
    } finally {
      setSorting(false);
    }
  };

  const handleOptimizeRoute = async () => {
    if (!compilationId) return;
    setOptimizing(true);
    try {
      const optimized = await attractionsApi.optimizeRoute(compilationId);
      toast.success('Itinéraire optimisé 🗺️');
      setBudgetTotal(optimized.total_budget);
    } catch (err) {
      toast.error("Erreur d'optimisation");
      console.error(err);
    } finally {
      setOptimizing(false);
    }
  };

  const handleClear = async () => {
    await clearAttractions();
    setBudgetTotal(null);
  };

  return (
    <div className="px-6 py-10 min-h-screen bg-gradient-to-b from-gray-50 to-white">
      <motion.h1
        className="text-3xl font-bold mb-6 text-center text-blue-600"
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
      >
        🧭 Ma Compilation
      </motion.h1>

      {selectedAttractions.length === 0 ? (
        <p className="text-center text-gray-500">Aucune attraction ajoutée pour le moment.</p>
      ) : (
        <>
          <div className="flex flex-wrap justify-center gap-4 mb-6">
            <button
              onClick={handleSortByBudget}
              disabled={sorting}
              className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-xl shadow hover:bg-blue-600 transition"
            >
              {sorting ? <Loader2 className="animate-spin" size={18} /> : <ArrowDownUp size={18} />}
              Trier par budget
            </button>

            <button
              onClick={handleOptimizeRoute}
              disabled={optimizing}
              className="flex items-center gap-2 px-4 py-2 bg-green-500 text-white rounded-xl shadow hover:bg-green-600 transition"
            >
              {optimizing ? <Loader2 className="animate-spin" size={18} /> : <Map size={18} />}
              Optimiser le parcours
            </button>

            <button
              onClick={handleClear}
              className="flex items-center gap-2 px-4 py-2 bg-red-500 text-white rounded-xl shadow hover:bg-red-600 transition"
            >
              <Trash2 size={18} /> Vider
            </button>
          </div>

          {budgetTotal && (
            <div className="text-center mb-4">
              <motion.p
                initial={{ scale: 0.8, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                className="text-lg font-semibold text-gray-700"
              >
                💰 Budget total estimé : <span className="text-blue-600">{budgetTotal.toFixed(2)} €</span>
              </motion.p>
            </div>
          )}

          <AttractionsCarousel attractions={selectedAttractions} />
        </>
      )}
    </div>
  );
}
