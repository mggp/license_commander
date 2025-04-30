const API_BASE_URL = 'http://localhost:8000';

export interface Application {
  id: number;
  name: string;
  type: string;
}

export interface PaginatedResponse {
  items: Application[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface TypeStats {
  type: string;
  count: number;
}

export interface ApplicationSummary {
  productividad: number;
  diseno: number;
  comunicacion: number;
  desarrollo: number;
  finanzas: number;
  marketing: number;
}

export const getApplications = async (page: number = 1, size: number = 10): Promise<PaginatedResponse> => {
  const response = await fetch(`${API_BASE_URL}/applications?page=${page}&size=${size}`);
  if (!response.ok) {
    throw new Error('Error al obtener las aplicaciones');
  }
  return response.json();
};

export const getApplicationsByType = async (type: string, page: number = 1, size: number = 10): Promise<PaginatedResponse> => {
  const response = await fetch(`${API_BASE_URL}/applications/type/${type}?page=${page}&size=${size}`);
  if (!response.ok) {
    throw new Error('Error al obtener las aplicaciones por tipo');
  }
  return response.json();
};

export const getApplicationStats = async (): Promise<TypeStats[]> => {
  const response = await fetch(`${API_BASE_URL}/applications/summary`);
  if (!response.ok) {
    throw new Error('Error al obtener las estadísticas de aplicaciones');
  }
  const summary: ApplicationSummary = await response.json();
  
  return Object.entries(summary).map(([type, count]) => ({
    type,
    count
  }));
}; 