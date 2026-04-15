import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { mapApi } from '../../../entities/map/api/map-api';
import { dashboardApi } from '../../../shared/api/base-api';
import { CityMap } from '../../../widgets/city-map/ui/CityMap';
import { TopBar } from '../../../widgets/top-bar/ui/TopBar';
import { BottomNav } from '../../../widgets/bottom-nav/ui/BottomNav';
import { ToastContainer } from '../../../shared/ui/toast';
import { useUserStore } from '../../../entities/user/model/store';
import type { MapTerritory } from '../../../entities/map/model/types';
import { Sword, Lock, MapPin } from 'lucide-react';
import { ROUTES } from '../../../shared/config/routes';

export const MapPage: React.FC = () => {
  const navigate = useNavigate();
  const setUser = useUserStore((state) => state.setUser);
  const [selectedTerritory, setSelectedTerritory] = useState<MapTerritory | null>(null);

  const { data: mapData, isLoading, error } = useQuery({
    queryKey: ['city-map'],
    queryFn: mapApi.getMap,
  });

  const { data: dashboard } = useQuery({
    queryKey: ['dashboard'],
    queryFn: dashboardApi.getDashboard,
  });

  React.useEffect(() => {
    if (dashboard) {
      setUser({
        id: dashboard.user_id,
        telegram_id: dashboard.telegram_id,
        username: dashboard.username,
        resources: dashboard.resources,
      });
    }
  }, [dashboard, setUser]);

  const handleTerritoryClick = (territory: MapTerritory) => {
    setSelectedTerritory(territory);
  };

  const handleCloseDetail = () => {
    setSelectedTerritory(null);
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-gray-400">Загрузка карты...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-red-400">Ошибка: {(error as Error).message}</div>
      </div>
    );
  }

  const territories = mapData?.territories || [];
  const capturedCount = territories.filter((t: MapTerritory) => t.is_mine).length;
  const totalIncomeMoney = territories
    .filter((t: MapTerritory) => t.is_mine)
    .reduce((sum: number, t: MapTerritory) => sum + (t.passive_income_money || 0), 0);
  const totalIncomeInfluence = territories
    .filter((t: MapTerritory) => t.is_mine)
    .reduce((sum: number, t: MapTerritory) => sum + (t.passive_income_influence || 0), 0);

  return (
    <div className="min-h-screen bg-gray-900 relative">
      <TopBar />
      <ToastContainer />

      {/* Stats bar */}
      <div className="flex items-center justify-between px-4 py-2 bg-gray-800/50 border-b border-gray-800">
        <span className="text-xs text-gray-400">
          Захвачено: {capturedCount}/{territories.length}
        </span>
        <div className="flex items-center gap-3">
          <span className="text-xs text-yellow-400">
            💰 +{totalIncomeMoney}/тик
          </span>
          <span className="text-xs text-blue-400">
            🌐 +{totalIncomeInfluence}/тик
          </span>
        </div>
      </div>

      {/* SVG City Map — responsive container with 4:3 aspect ratio */}
      <div className="w-full max-w-2xl mx-auto px-2 py-4">
        <div className="relative w-full" style={{ aspectRatio: '4/3' }}>
          <CityMap
            territories={territories}
            onTerritoryClick={handleTerritoryClick}
          />
        </div>
      </div>

      {/* Territory detail panel (slide up) */}
      {selectedTerritory && (
        <div className="fixed bottom-0 left-0 right-0 z-40 pb-16" style={{ paddingBottom: 'calc(3.5rem + var(--safe-area-inset-bottom, 0px))' }}>
          <div className="bg-gray-900 border-t border-gray-800 p-4 rounded-t-2xl shadow-2xl max-h-[50vh] overflow-y-auto mx-auto max-w-lg">
            <div className="flex items-start justify-between mb-3">
              <div>
                <h3 className="font-bold text-white text-lg">{selectedTerritory.name}</h3>
                <p className="text-xs text-gray-400 capitalize">
                  {selectedTerritory.territory_type}
                </p>
              </div>
              <button
                onClick={handleCloseDetail}
                className="text-gray-400 hover:text-white p-1"
              >
                ✕
              </button>
            </div>

            <p className="text-sm text-gray-300 mb-3">
              {selectedTerritory.description}
            </p>

            {/* Requirements */}
            <div className="grid grid-cols-3 gap-2 mb-3 text-center">
              <div className="bg-gray-800 rounded p-2">
                <div className="text-xs text-red-400 font-bold">
                  💪 {selectedTerritory.power_required || 20}
                </div>
                <div className="text-[10px] text-gray-500">Сила</div>
              </div>
              <div className="bg-gray-800 rounded p-2">
                <div className="text-xs text-blue-400 font-bold">
                  🧠 {selectedTerritory.intellect_required || 15}
                </div>
                <div className="text-[10px] text-gray-500">Интеллект</div>
              </div>
              <div className="bg-gray-800 rounded p-2">
                <div className="text-xs text-green-400 font-bold">
                  ⚡ {selectedTerritory.agility_required || 15}
                </div>
                <div className="text-[10px] text-gray-500">Ловкость</div>
              </div>
            </div>

            {/* Income */}
            <div className="flex items-center gap-4 mb-3 text-sm">
              <span className="text-yellow-400">
                💰 +{selectedTerritory.passive_income_money || 50}/тик
              </span>
              <span className="text-blue-400">
                🌐 +{selectedTerritory.passive_income_influence || 1}/тик
              </span>
            </div>

            {/* Boss info */}
            {!selectedTerritory.is_mine && selectedTerritory.boss && (
              <div className="mb-3 p-2 bg-gray-800 rounded flex items-center gap-2">
                <Sword className="w-4 h-4" style={{ color: selectedTerritory.boss.color }} />
                <span className="text-sm text-gray-300">
                  Владелец: <strong style={{ color: selectedTerritory.boss.color }}>
                    {selectedTerritory.boss.name}
                  </strong>
                </span>
              </div>
            )}

            {/* Action button */}
            {selectedTerritory.is_mine ? (
              <button
                className="w-full py-3 bg-blue-600 hover:bg-blue-500 text-white font-bold rounded-lg flex items-center justify-center gap-2 active:bg-blue-700"
                onClick={() => {
                  setSelectedTerritory(null);
                  navigate(`${ROUTES.TERRITORIES}/${selectedTerritory.id}`);
                }}
              >
                <MapPin className="w-5 h-5" />
                Открыть район
              </button>
            ) : selectedTerritory.boss ? (
              <button
                className="w-full py-3 bg-red-600 hover:bg-red-500 text-white font-bold rounded-lg flex items-center justify-center gap-2 active:bg-red-700"
                onClick={() => {
                  // TODO: navigate to district screen
                  alert(`Переход к району: ${selectedTerritory.name}`);
                }}
              >
                <Sword className="w-5 h-5" />
                Захватить район
              </button>
            ) : (
              <div className="w-full py-3 bg-gray-800 text-gray-500 font-bold rounded-lg flex items-center justify-center gap-2 cursor-not-allowed">
                <Lock className="w-4 h-4" />
                Нужно 🌐 {selectedTerritory.influence_required || 25} влияния
              </div>
            )}
          </div>
        </div>
      )}

      <BottomNav />
    </div>
  );
};
