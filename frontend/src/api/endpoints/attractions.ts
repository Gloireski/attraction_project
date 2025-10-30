// api/endpoints/attractions.ts attractions API endpoints
import { apiClient } from '../client'
import type { Attraction, AttractionResponse } from '../types/attraction'

export const attractionsApi = {
  // Get all attractions
  getAll: async (params?: { search?: string; limit?: number }): Promise<AttractionResponse> => {
    const { data } = await apiClient.get('/attractions/', { params })
    return data
  },

  // Get single attraction
  getById: async (id: string): Promise<Attraction> => {
    const { data } = await apiClient.get(`/attractions/${id}/`)
    return data
  },

  // Search attractions
  search: async (query: string): Promise<AttractionResponse> => {
    const { data } = await apiClient.get('/attractions/search/', {
      params: { q: query }
    })
    return data
  },

  // Get nearby attractions
  getNearby: async (lat: number, lng: number, radius: number = 10): Promise<AttractionResponse> => {
    const { data } = await apiClient.get('/attractions/nearby/', {
      params: { lat, lng, radius }
    })
    return data
  },

  // Create attraction (example mutation)
  create: async (attraction: Omit<Attraction, 'id'>): Promise<Attraction> => {
    const { data } = await apiClient.post('/attractions/', attraction)
    return data
  },
}