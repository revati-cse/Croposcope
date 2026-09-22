import axios, { AxiosResponse } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// API functions
export const authAPI = {
  login: (credentials: { username: string; password: string }) =>
    api.post('/auth/login', credentials),
  
  register: (userData: { username: string; email: string; password: string; name: string }) =>
    api.post('/auth/register', userData),
  
  logout: () => api.post('/auth/logout'),
  
  getProfile: () => api.get('/auth/profile'),
};

export const analysisAPI = {
  uploadAndAnalyze: (formData: FormData) =>
    api.post('/analysis/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  
  getHistory: (page = 1, perPage = 10) =>
    api.get(`/analysis/history?page=${page}&per_page=${perPage}`),
  
  getAnalysis: (id: number) => api.get(`/analysis/${id}`),
  
  updateTreatment: (id: number, data: { treatment_applied: boolean; notes?: string }) =>
    api.put(`/analysis/${id}/treatment`, data),
  
  getAnalytics: () => api.get('/analysis/analytics'),
  
  deleteAnalysis: (id: number) => api.delete(`/analysis/${id}`),
};

export const treatmentAPI = {
  getTreatments: (filters?: { disease?: string; crop?: string; type?: string }) =>
    api.get('/treatments', { params: filters }),
  
  searchTreatments: (query: string) =>
    api.get(`/treatments/search?q=${encodeURIComponent(query)}`),
  
  getTreatment: (id: number) => api.get(`/treatments/${id}`),
};

export const voiceAPI = {
  processCommand: (data: { transcript: string; language: string }) =>
    api.post('/voice/process', data),
  
  getInteractions: (page = 1) =>
    api.get(`/voice/interactions?page=${page}`),
  
  synthesizeSpeech: (text: string, language = 'en') =>
    api.post('/voice/synthesize', { text, language }, { responseType: 'blob' }),
};

export default api;