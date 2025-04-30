export const formatApplicationType = (type: string): string => {
  const typeMap: Record<string, string> = {
    productividad: 'Productividad',
    diseno: 'Diseño',
    comunicacion: 'Comunicación',
    desarrollo: 'Desarrollo',
    finanzas: 'Finanzas',
    marketing: 'Marketing'
  };

  return typeMap[type] || type;
}; 