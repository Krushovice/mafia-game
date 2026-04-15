import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { dashboardApi } from '../../../shared/api/base-api';
import { Header } from '../../../widgets/header/ui/Header';
import { ResourceBar } from '../../../widgets/resource-bar/ui/ResourceBar';
import { MissionCard } from '../../../widgets/mission-card/ui/MissionCard';
import { useNavigate } from 'react-router-dom';
import { ROUTES } from '../../../shared/config/routes';

export const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const { data: dashboard, isLoading, error } = useQuery({
    queryKey: ['dashboard'],
    queryFn: dashboardApi.getDashboard,
  });

  if (isLoading) {
    return <div className="text-center mt-10 text-gray-400">Загрузка...</div>;
  }

  if (error) {
    return <div className="text-center mt-10 text-red-500">Ошибка: {(error as Error).message}</div>;
  }

  if (!dashboard) {
    return <div className="text-center mt-10 text-gray-400">Нет данных</div>;
  }

  const { available_missions, territories } = dashboard;

  return (
    <div className="min-h-screen bg-gray-900 text-white p-4 font-sans">
      <Header />
      <ResourceBar />

      {/* Missions */}
      <section className="mb-6">
        <div className="flex justify-between items-center mb-3">
          <h2 className="text-xl font-bold">🗺️ Миссии</h2>
          <button
            className="text-sm text-blue-400 hover:text-blue-300"
            onClick={() => navigate(ROUTES.MISSIONS)}
          >
            Все миссии →
          </button>
        </div>
        {available_missions.length > 0 ? (
          <div className="space-y-3">
            {available_missions.slice(0, 3).map((m) => (
              <MissionCard
                key={m.id}
                mission={m}
                onStart={() => navigate(ROUTES.MISSIONS)}
              />
            ))}
          </div>
        ) : (
          <p className="text-gray-500 text-center py-4">Нет доступных миссий</p>
        )}
      </section>

      {/* Territories */}
      <section>
        <div className="flex justify-between items-center mb-3">
          <h2 className="text-xl font-bold">🏘️ Территории</h2>
          <button
            className="text-sm text-blue-400 hover:text-blue-300"
            onClick={() => navigate(ROUTES.TERRITORIES)}
          >
            Карта →
          </button>
        </div>
        <div className="bg-gray-800 p-4 rounded-lg">
          <div className="flex justify-between items-center mb-2">
            <span className="text-gray-300">Захвачено:</span>
            <span className="font-bold">{territories.length}</span>
          </div>
          {territories.length > 0 && (
            <div className="text-sm text-gray-400">
              Доход: +{territories.reduce((sum, t) => sum + t.passive_income_money, 0)}💰/тик
            </div>
          )}
        </div>
      </section>
    </div>
  );
};
