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

export const getApplications = async (page: number = 1, size: number = 10): Promise<PaginatedResponse> => {
  const response = await fetch(`${API_BASE_URL}/applications?page=${page}&size=${size}`);
  if (!response.ok) {
    throw new Error('Error al obtener las aplicaciones');
  }
  return response.json();
}; 