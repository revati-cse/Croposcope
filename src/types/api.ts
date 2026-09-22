// Base API response types
export interface ApiResponse<T = any> {
  data: T;
  message?: string;
  status: 'success' | 'error';
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
}

// Authentication types
export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
  name: string;
}

export interface AuthResponse {
  access_token: string;
  user: User;
}

export interface User {
  id: number;
  username: string;
  email: string;
  name: string;
  avatar?: string;
  preferences: UserPreferences;
  created_at: string;
}

export interface UserPreferences {
  language: string;
  theme: string;
  notifications: boolean;
}

// Analysis types
export interface CropAnalysis {
  id: number;
  crop_type: string;
  disease_detected: string;
  confidence_score: number;
  severity_level: 'low' | 'medium' | 'high';
  field_location?: string;
  treatment_applied: boolean;
  notes?: string;
  model_version: string;
  processing_time: number;
  created_at: string;
  image_path: string;
}

export interface AnalysisRequest {
  image: File;
  crop_type?: string;
  field_location?: string;
  notes?: string;
}

export interface AnalysisResponse {
  analysis_id: number;
  crop: string;
  disease: string;
  confidence: number;
  severity: 'low' | 'medium' | 'high';
  processing_time: number;
  model_version: string;
  all_predictions: PredictionResult[];
  created_at: string;
}

export interface PredictionResult {
  crop: string;
  disease: string;
  confidence: number;
}

// Treatment types
export interface Treatment {
  id: number;
  name: string;
  disease_target: string;
  crop_target: string;
  treatment_type: 'organic' | 'biological' | 'cultural' | 'preventive';
  effectiveness_rating: number;
  duration: string;
  difficulty_level: 'easy' | 'medium' | 'hard';
  ingredients: string[];
  instructions: string[];
  benefits: string[];
  precautions: string[];
  cost_level: 'low' | 'medium' | 'high';
  seasonal_info: string[];
  created_at: string;
}

// Voice types
export interface VoiceCommand {
  transcript: string;
  language: string;
  command_type?: string;
}

export interface VoiceResponse {
  response_text: string;
  command_type: string;
  success: boolean;
}

export interface VoiceInteraction {
  id: number;
  transcript: string;
  language_code: string;
  command_type?: string;
  response_text?: string;
  created_at: string;
}

// Analytics types
export interface AnalyticsData {
  total_analyses: number;
  disease_detected: number;
  average_confidence: number;
  treatment_compliance: number;
  disease_distribution: Record<string, number>;
  crop_distribution: Record<string, number>;
  severity_distribution: Record<string, number>;
}

// Error types
export interface ApiError {
  message: string;
  code?: string;
  details?: any;
}
