import { useQuery } from '@tanstack/react-query';
import api from '../services/api';

export const useAttractions = () => {
  return useQuery(['attractions'], async () => {
    const { data } = await api.get('attractions/');
    return data;
  });
};
