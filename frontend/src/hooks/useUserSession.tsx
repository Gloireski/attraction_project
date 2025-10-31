'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'react-hot-toast';
import api from '@/api/attractions';
import type { UserSession } from '@/types/user';

// Récupérer la session actuelle
export const useUserSession = () => {
  return useQuery({
    queryKey: ['userSession'],
    queryFn: async (): Promise<UserSession> => {
      const res = await api.get('/api/users/get_session/');
      console.log("get session attempt", res.status)

     if (!res.statusText) {
      throw new Error('Network response was not ok')
    }
      return res.data;
    },
    retry: false,
    // staleTime: 1000 * 60 * 5, // 5 minutes
    
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

  return useMutation({
    mutationFn: async () => {
      const res = await api.post('/api/users/logout/');
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['userSession']}); // vider le cache
    //   queryClient.removeQueries()?
      toast.success('Déconnecté avec succès !');
    },
    onError: (err: Error) => {
      console.error('Erreur logout:', err);
      toast.error('Impossible de se déconnecter.');
    },
  });
};
