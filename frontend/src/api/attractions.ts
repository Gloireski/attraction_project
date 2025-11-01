import axios from 'axios';
import type { Attraction } from '@/types/attractions';

const serverUrl = "http://127.0.0.1:8000"

const api = axios.create({
  baseURL: serverUrl,
  withCredentials: true,  // indispensable
});

export const attractionsApi = {
  getPopular: async (country: string): Promise<Attraction[]> => {
    const res = await api.get(`/api/attractions_v1/popular/?country=${country}`);
    return res.data;
  },

  getPopularByTypeAndRegion: async(country: string, capital: string, profile_type: string): Promise<Attraction[]> => {
    const res = await api.get(`/api/attractions_v1/search_default/?country=${country}&capital=${capital}&profile_type=${profile_type}`)
    return res.data
  },

  compileAttraction: async (id: number) => {
    const res = await api.post(`/api//compilation/add/${id}`);
    return res.data;
  },

  getAttractionDetail: async (id: string) => {
    const res = await api.get(`/api//attractions_v1/${id}`);
    return res.data;
  },

  // --- COMPILATIONS ---
  getUserCompilations: async () => {
    const res = await api.get(`/api/compilation/`);
    return res.data;
  },

  createCompilation: async () => {
    const res = await api.post(`/api/compilation/create/`);
    return res.data;
  },

  addToCompilation: async (compilationId: number, attractionId: number) => {
    const res = await api.post(`/api/compilation/${compilationId}/add_attraction/`, { attraction_id: attractionId });
    return res.data;
  },

  removeFromCompilation: async (compilationId: number, attractionId: number) => {
    const res = await api.post(`/api/compilation/${compilationId}/remove_attraction/`, { attraction_id: attractionId });
    return res.data;
  },

  optimizeRoute: async (compilationId: number) => {
    const res = await api.post(`/api/compilation/${compilationId}/optimize_route/`);
    return res.data;
  },

  sortByBudget: async (compilationId: number) => {
    const res = await api.post(`/api/compilation/${compilationId}/sort_by_budget/`);
    return res.data;
  },
};
 

export default api;