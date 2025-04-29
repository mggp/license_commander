const API_BASE_URL = 'http://localhost:8000';

export interface Application {
  id: number;
  name: string;
  type: string;
}

export const getApplications = async (): Promise<Application[]> => {
  const response = await fetch(`${API_BASE_URL}/applications`);
  if (!response.ok) {
    throw new Error('Error al obtener las aplicaciones');
  }
  return response.json();
}; 