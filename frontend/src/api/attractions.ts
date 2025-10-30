import axios from 'axios';
import type { Attraction } from '@/types/attractions';

const serverUrl = "http://127.0.0.1:8000"

const api = axios.create({
  baseURL: serverUrl,
});

export const attractionsApi = {
  getPopular: async (country: string): Promise<Attraction[]> => {
    const res = await api.get(`/api/attractions_v1/popular/?country=${country}`);
    return res.data;
  },

  compileAttraction: async (id: number) => {
    const res = await api.post(`/api//compilation/add/${id}`);
    return res.data;
  },

  getAttractionDetail: async (id: string) => {
    const res = await api.get(`/api//attractions_v1/${id}`);
    return res.data;
  },

  optimizeRoute: async (compilationId: string) => {
    const res = await api.post(`/api/compilation/${compilationId}/optimize`);
    return res.data;
  },
};
