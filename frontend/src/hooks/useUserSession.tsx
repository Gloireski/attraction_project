'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'react-hot-toast';
import { api } from '@/lib/api';
import type { UserSession } from '@/types/user';
import { useRouter, usePathname } from 'next/navigation';

// Récupérer la session actuelle
export const useUserSession = () => {
  const router = useRouter();
  const pathname = usePathname();

  return useQuery({
    queryKey: ['userSession'],
    queryFn: async (): Promise<UserSession> => {
    try {
        const res = await api.get('/api/users/get_session/');
        if (res.status !== 200) {
          throw new Error('Session not found');
        }
        return res.data;
      } catch (error: any) {
        console.error('Erreur récupération session:', error);
         // Rediriger seulement si on est sur "/" ou "/search"
        if (pathname === '/home' || pathname === '/search') {
          router.push('/'); // ou autre route si besoin
        }
        // router.push('/'); // redirect to home if no session
        throw error;
      }
    },
    // retry: false,
    staleTime: 1000 * 60 * 5, // 5 minutes
    
    // onError: (err: any) => {
    //   console.error('Erreur récupération session:', err);
    // },
  });
};

// Créer ou mettre à jour la session utilisateur
export const useCreateUserSession = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (payload: { profile_type: string; country: string}): Promise<UserSession> => {
        console.log('params ', payload)
        const res = await api.post('/api/users/create_session/', payload);
        return res.data;
    },
    onSuccess: (data) => {
      queryClient.setQueryData(['userSession'], data); // mettre à jour le cache
      toast.success('Session créée !');
    },
    onError: (err: Error) => {
      console.error('Erreur création session:', err);
      toast.error('Impossible de créer la session.');
    },
  });
};

// Déconnexion utilisateur
export const useLogoutUser = () => {
  const queryClient = useQueryClient();
  const router = useRouter();

  return useMutation({
    mutationFn: async () => {
      const res = await api.post('/api/users/logout/');
      return res.data;
    },
    onSuccess: () => {
      console.log('deconnexion')
      router.push('/');
      queryClient.setQueryData(['userSession'], null); // <-- important
      // queryClient.invalidateQueries({ queryKey: ['userSession']}); // vider le cache
      // queryClient.refetchQueries({ queryKey: ['userSession'] }); // <-- force refetch
    //   queryClient.removeQueries()?
      toast.success('Déconnecté avec succès !');
    },
    onError: (err: Error) => {
      console.error('Erreur logout:', err);
      toast.error('Impossible de se déconnecter.');
    },
  });
};
