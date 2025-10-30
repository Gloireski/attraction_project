import axios from 'axios';
import type { Attraction } from '@/types/attractions';

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000/api',
});

export const attractionsApi = {
  getPopular: async (country: string): Promise<Attraction[]> => {
    const res = await api.get(`/attractions_v1/popular?country=${country}`);
    return res.data;
  },

  compileAttraction: async (id: number) => {
    const res = await api.post(`/compilation/add/${id}`);
    return res.data;
  },

  getAttractionDetail: async (id: string) => {
    const res = await api.get(`/attractions_v1/${id}`);
    return res.data;
  },

  optimizeRoute: async (compilationId: string) => {
    const res = await api.post(`/compilation/${compilationId}/optimize`);
    return res.data;
  },
};
