export interface AnalysisFormData {
  image: File | null;
  cropType: string;
  fieldLocation: string;
  notes: string;
}

export interface AnalysisFilter {
  crop?: string;
  disease?: string;
  severity?: 'low' | 'medium' | 'high';
  dateFrom?: string;
  dateTo?: string;
  treatmentStatus?: 'applied' | 'pending' | 'all';
}

export interface AnalysisStats {
  totalAnalyses: number;
  diseaseDetected: number;
  averageConfidence: number;
  treatmentCompliance: number;
}

export interface ChartData {
  name: string;
  value: number;
  color?: string;
}

export interface TrendData {
  date: string;
  analyses: number;
  diseases: number;
  confidence: number;
}