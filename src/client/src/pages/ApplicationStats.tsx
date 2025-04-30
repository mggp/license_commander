import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getApplicationStats } from '../services/api';
import { formatApplicationType } from '../utils/formatType';

interface TypeStats {
  type: string;
  count: number;
}

export default function ApplicationStats() {
  const [stats, setStats] = useState<TypeStats[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await getApplicationStats();
        setStats(response);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Error desconocido');
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
        <strong className="font-bold">Error: </strong>
        <span className="block sm:inline">{error}</span>
      </div>
    );
  }

  return (
    <div className="bg-white shadow rounded-lg p-6">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">
        Estadísticas de Aplicaciones
      </h1>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {stats.map((stat) => (
          <div key={stat.type} className="bg-white overflow-hidden shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <Link
                to={`/type/${stat.type}`}
                className="text-lg font-medium text-indigo-600 hover:text-indigo-900"
              >
                {formatApplicationType(stat.type)}
              </Link>
              <p className="mt-2 text-3xl font-semibold text-gray-900">
                {stat.count}
              </p>
              <p className="mt-1 text-sm text-gray-500">
                aplicaciones
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
} 