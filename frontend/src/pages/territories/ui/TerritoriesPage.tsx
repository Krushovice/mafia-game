// @ts-nocheck
import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { territoryApi } from '../../../entities/territory/api/territory-api';
import { Header } from '../../../widgets/header/ui/Header';
import { ResourceBar } from '../../../widgets/resource-bar/ui/ResourceBar';
import { Card } from '../../../shared/ui/card/Card';
import { Button } from '../../../shared/ui/button/Button';
import { showConfirm } from '../../../shared/lib/telegram/telegram';

export const TerritoriesPage: React.FC = () => {
  const { data: territories, isLoading, error } = useQuery({
    queryKey: ['territories'],
    queryFn: territoryApi.getAll,
  });

  const handleCapture = async (territory: any) => {
    if (!territory.can_attempt) {
      await showConfirm(
        `Нужно ${territory.influence_required} влияния для захвата ${territory.name}`
      );
      return;
    }
    const confirmed = await showConfirm(
      `Начать захват ${territory.name}?\nТребования: 💪${territory.power_required} | 🧠${territory.intellect_required} | ⚡${territory.agility_required}`
    );
    if (confirmed) {
      await territoryApi.capture(territory.id);
    }
  };

  if (isLoading) {
    return <div className="text-center mt-10 text-gray-400">Загрузка...</div>;
  }

  if (error) {
    return <div className="text-center mt-10 text-red-500">Ошибка: {(error as Error).message}</div>;
  }

  const myTerritories = territories?.filter((t: any) => t.is_captured) || [];
  const availableTerritories = territories?.filter((t: any) => !t.is_captured) || [];

  return (
    <div className="min-h-screen bg-gray-900 text-white p-4 font-sans pb-16">
      <Header />
      <ResourceBar />

      <h2 className="text-xl font-bold mb-4">🗺️ Карта территорий</h2>

      {myTerritories.length > 0 && (
        <section className="mb-6">
          <h3 className="text-lg font-bold mb-2 text-green-400">🟢 Мои территории ({myTerritories.length})</h3>
          <div className="space-y-3">
            {myTerritories.map((t: any) => (
              <Card key={t.id} className="border-green-800">
                <h3 className="font-bold text-lg">{t.name}</h3>
                <div className="text-sm text-gray-400 mb-2 capitalize">{t.territory_type}</div>
                <div className="text-sm text-green-300">
                  Доход: +{t.passive_income_money}💰 | +{t.passive_income_influence}🌐 / тик
                </div>
              </Card>
            ))}
          </div>
        </section>
      )}

      <section>
        <h3 className="text-lg font-bold mb-2 text-gray-300">🔴 Свободные территории ({availableTerritories.length})</h3>
        <div className="space-y-3">
          {availableTerritories.map((t: any) => (
            <Card key={t.id}>
              <div className="flex justify-between items-start mb-2">
                <div>
                  <h3 className="font-bold text-lg">{t.name}</h3>
                  <p className="text-sm text-gray-400 capitalize">{t.territory_type}</p>
                </div>
                <span className={`text-xs px-2 py-1 rounded ${
                  t.can_attempt ? 'bg-blue-900 text-blue-200' : 'bg-gray-700 text-gray-500'
                }`}>
                  {t.can_attempt ? 'Доступна' : `Нужно ${t.influence_required}🌐`}
                </span>
              </div>

              <div className="text-sm text-gray-300 mb-2">
                <div className="flex justify-between">
                  <span>💪 {t.power_required}</span>
                  <span>🧠 {t.intellect_required}</span>
                  <span>⚡ {t.agility_required}</span>
                </div>
              </div>

              <div className="text-sm text-gray-400 mb-3">
                Доход: +{t.passive_income_money}💰 | +{t.passive_income_influence}🌐 / тик
              </div>

              <Button
                variant={t.can_attempt ? 'primary' : 'secondary'}
                size="sm"
                disabled={!t.can_attempt}
                onClick={() => handleCapture(t)}
                className="w-full"
              >
                {t.can_attempt ? '⚔️ Захватить' : `🔒 Нужно ${t.influence_required} влияния`}
              </Button>
            </Card>
          ))}
        </div>
      </section>
    </div>
  );
};
