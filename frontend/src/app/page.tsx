'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import ProfileSelector from '@/components/ProfileSelector';
import CountrySelector from '@/components/CountrySelector';
import { useCreateUserSession } from '@/hooks/useUserSession';

import { i } from 'framer-motion/m';

export default function LandingPage() {
  const [role, setRole] = useState<string | null>(null);
  const [country, setCountry] = useState<string>('');
  const router = useRouter();

  // const createSession = useCreateUserSession();
  const { mutateAsync: createSession } = useCreateUserSession();

  // const handleSubmit = () => {
  //   if (role && country) {
  //     router.push(`/home?country=${country}&role=${role}`);
  //   }
  // };

  const handleSubmit = async () => {
    if (!role || !country) return;

    try{
        await createSession({ profile_type: role, country });
        router.push(`/home?country=${country}&role=${role}`);
      } catch (err) {
        console.error('Erreur lors de la création de la session', err);
      }
  };

  return (
    <main className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-b from-blue-100 to-white px-6">
      <h1 className="text-4xl font-bold text-primary mb-8">🌍 ExploreNow</h1>
      <p className="text-gray-600 mb-6">Découvrez les attractions les plus populaires selon votre profil.</p>

    <ProfileSelector selected={role} onSelect={setRole} />
        <div className="mt-6 w-full max-w-sm">
          <CountrySelector value={country} onChange={setCountry} />
        </div>

        <button
          disabled={!role || !country || createSession.isLoading}
          onClick={handleSubmit}
          className="mt-10 px-8 py-3 bg-primary text-white font-semibold rounded-xl hover:bg-blue-700 transition disabled:opacity-50"
        >
       {createSession.isLoading ? 'Chargement...' : 'Explorer'}
      </button>
    </main>
  );
}
