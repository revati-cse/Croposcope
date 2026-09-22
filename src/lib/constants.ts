export const APP_CONFIG = {
  name: 'Croposcope',
  version: '1.0.0',
  description: 'AI-Powered Crop Disease Detection & Organic Treatment Solutions',
  author: 'Croposcope Team',
};

export const API_ENDPOINTS = {
  BASE_URL: import.meta.env.VITE_API_URL || 'http://localhost:5000/api',
  AUTH: {
    LOGIN: '/auth/login',
    REGISTER: '/auth/register',
    LOGOUT: '/auth/logout',
    PROFILE: '/auth/profile',
  },
  ANALYSIS: {
    UPLOAD: '/analysis/upload',
    HISTORY: '/analysis/history',
    ANALYTICS: '/analysis/analytics',
  },
  TREATMENTS: '/treatments',
  VOICE: '/voice',
};

export const SUPPORTED_LANGUAGES = [
  { code: 'en-US', name: 'English', flag: '🇺🇸', rtl: false },
  { code: 'ta-IN', name: 'Tamil', flag: '🇮🇳', rtl: false },
  { code: 'hi-IN', name: 'Hindi', flag: '🇮🇳', rtl: false },
  { code: 'ur-PK', name: 'Urdu', flag: '🇵🇰', rtl: true },
];

export const DISEASE_SEVERITY_COLORS = {
  low: 'bg-green-100 text-green-800 dark:bg-green-900/20',
  medium: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20',
  high: 'bg-red-100 text-red-800 dark:bg-red-900/20',
};

export const TREATMENT_TYPE_COLORS = {
  organic: 'bg-green-100 text-green-800 dark:bg-green-900/20',
  biological: 'bg-blue-100 text-blue-800 dark:bg-blue-900/20',
  cultural: 'bg-purple-100 text-purple-800 dark:bg-purple-900/20',
  preventive: 'bg-orange-100 text-orange-800 dark:bg-orange-900/20',
};

export const FILE_UPLOAD = {
  MAX_SIZE: 16 * 1024 * 1024, // 16MB
  ALLOWED_TYPES: ['image/jpeg', 'image/png', 'image/webp', 'image/bmp'],
  ALLOWED_EXTENSIONS: ['.jpg', '.jpeg', '.png', '.webp', '.bmp'],
};

export const VOICE_CONFIG = {
  RECOGNITION: {
    CONTINUOUS: true,
    INTERIM_RESULTS: true,
    MAX_ALTERNATIVES: 1,
  },
  SYNTHESIS: {
    RATE: 0.9,
    PITCH: 1,
    VOLUME: 1,
  },
};

export const PAGINATION = {
  DEFAULT_PAGE_SIZE: 10,
  MAX_PAGE_SIZE: 100,
};