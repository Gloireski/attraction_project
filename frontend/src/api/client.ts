// api/client.ts axios instance with default config

import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
})

// TripAdvisor API key (avoid committing secrets in source code)
const TRIPADVISOR_API_KEY = "68D5DE3F05784D33B0A19D160EC022841"
export const tripAdvisorClient = axios.create({
  baseURL: 'https://api.content.tripadvisor.com/api/v1/location',
  headers: {
    'Content-Type': 'application/json',
    'X-TripAdvisor-API-Key': TRIPADVISOR_API_KEY,
  },
    timeout: 10000,
    })