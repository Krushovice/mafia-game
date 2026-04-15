import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { mapApi } from '../../../entities/map/api/map-api';
import { dashboardApi } from '../../../shared/api/base-api';
import { TopBar } from '../../../widgets/top-bar/ui/TopBar';
import { BottomNav } from '../../../widgets/bottom-nav/ui/BottomNav';
import { ToastContainer } from '../../../shared/ui/toast';
import { characterApi } from '../../../entities/character/api/character-api';
import { useStartMission } from '../../../features/start-mission/model/use-start-mission';
import type { MapTerritory } from '../../../entities/map/model/types';
import type { Character } from '../../../entities/character/model/types';
import { Sword, Target, DollarSign, Globe, ArrowLeft, Lock } from 'lucide-react';

/**
 * DistrictPage — детальный экран района.
 * Показывает мини-карту района с кружками миссий, информацию о районе,
 * и возможность запустить миссию или захватить район.
 */
export const DistrictPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [selectedMission, setSelectedMission] = useState<any | null>(null);
  const [selectedCharId, setSelectedCharId] = useState<number | null>(null);

  const { startMission, isLoading: isStarting } = useStartMission();

  const territoryId = id ? Number(id) : 0;

  // Load map data to find the territory
  const { data: mapData, isLoading: mapLoading } = useQuery({
    queryKey: ['city-map'],
    queryFn: mapApi.getMap,
  });

  const { data: dashboard } = useQuery({
    queryKey: ['dashboard'],
    queryFn: dashboardApi.getDashboard,
  });

  const { data: characters } = useQuery({
    queryKey: ['characters'],
    queryFn: characterApi.getAll,
  });

  const territory = mapData?.territories?.find(
    (t: MapTerritory) => t.id === territoryId
  );

  // Available missions on this territory (from dashboard)
  const allMissions = dashboard?.available_missions || [];
  // Filter missions by territory_id when backend provides it, otherwise show all
  const districtMissions = allMissions.filter(
    (m: any) => m.territory_id === null || m.territory_id === territoryId
  );

  const handleBack = () => navigate(-1);

  const handleStartMission = async (mission: any) => {
    setSelectedMission(mission);
    setSelectedCharId(null);
  };

  const handleConfirmStart = async () => {
    if (!selectedMission || !selectedCharId) return;
    try {
      await startMission(selectedMission.id, [selectedCharId]);
      setSelectedMission(null);
      setSelectedCharId(null);
    } catch (e) {
      // Error handled by hook
    }
  };

  if (mapLoading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center text-gray-400">
        Загрузка...
      </div>
    );
  }

  if (!territory) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center text-gray-400">
        Район не найден
      </div>
    );
  }

  const chars = characters || [];

  // Character selection modal
  if (selectedMission) {
    return (
      <div className="min-h-screen bg-gray-900 text-white p-4 font-sans">
        <TopBar />

        <div className="fixed inset-0 z-50 bg-black/80 flex items-end sm:items-center justify-center p-0 sm:p-4">
          <div className="bg-gray-900 rounded-t-2xl sm:rounded-2xl border border-gray-800 w-full sm:max-w-md max-h-[90vh] overflow-y-auto">
            <div className="p-4 border-b border-gray-800">
              <div className="font-bold text-white mb-1">{selectedMission.location_name}</div>
              <div className="text-sm text-gray-400">
                💰 {selectedMission.reward_money} | 🌐 {selectedMission.reward_influence ?? 0} | {selectedMission.difficulty}
              </div>
            </div>

            <div className="p-4">
              <h3 className="text-sm font-semibold text-gray-300 mb-3">Выбери бойца:</h3>
              {chars.length === 0 ? (
                <p className="text-gray-500 text-sm">У тебя нет бойцов</p>
              ) : (
                <div className="space-y-2">
                  {chars.map((char: Character) => (
                    <button
                      key={char.id}
                      className={`w-full p-3 rounded-lg border transition-all text-left ${
                        selectedCharId === char.id
                          ? 'border-blue-500 bg-blue-900/30'
                          : 'border-gray-700 bg-gray-800 hover:border-gray-600'
                      }`}
                      onClick={() => setSelectedCharId(char.id)}
                      disabled={char.is_busy}
                    >
                      <div className="flex items-center gap-3">
                        <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                          selectedCharId === char.id ? 'bg-blue-600' : char.is_busy ? 'bg-gray-600' : 'bg-gray-700'
                        }`}>
                          {char.is_busy ? '🔒' : '👤'}
                        </div>
                        <div className="flex-1">
                          <div className="font-bold text-white text-sm">{char.name}</div>
                          <div className="text-xs text-gray-400 capitalize">{char.role}</div>
                        </div>
                        {char.is_busy ? (
                          <span className="text-xs text-gray-500">Занят</span>
                        ) : (
                          <div className="flex gap-2 text-xs">
                            <span className="text-red-400">💪{char.power}</span>
                            <span className="text-blue-400">🧠{char.intellect}</span>
                            <span className="text-green-400">⚡{char.agility}</span>
                          </div>
                        )}
                      </div>
                    </button>
                  ))}
                </div>
              )}

              <button
                className="w-full mt-4 py-3 bg-blue-600 hover:bg-blue-500 disabled:bg-gray-700 disabled:text-gray-500 text-white font-bold rounded-lg transition-all"
                disabled={!selectedCharId || isStarting}
                onClick={handleConfirmStart}
              >
                {isStarting ? 'Начинаю...' : 'Начать миссию'}
              </button>
              <button
                className="w-full mt-2 py-3 bg-gray-700 hover:bg-gray-600 text-white font-bold rounded-lg transition-all"
                onClick={() => setSelectedMission(null)}
              >
                Отмена
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Mission circle colors by type
  function getMissionColor(mission: any): string {
    if (mission.mission_type === 'flash') return '#ef4444';
    if (mission.difficulty === 'hard') return '#f59e0b';
    if (mission.difficulty === 'medium') return '#3b82f6';
    return '#22c55e';
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white pb-16">
      <TopBar />
      <ToastContainer />

      {/* Header */}
      <div className="flex items-center gap-3 px-4 py-3 bg-gray-800/50 border-b border-gray-800">
        <button onClick={handleBack} className="text-gray-400 hover:text-white">
          <ArrowLeft className="w-5 h-5" />
        </button>
        <div>
          <h1 className="font-bold text-lg">{territory.name}</h1>
          <p className="text-xs text-gray-400 capitalize">{territory.territory_type}</p>
        </div>
        {territory.is_mine && (
          <span className="ml-auto text-xs bg-green-800 text-green-200 px-2 py-1 rounded-full">
            ✅ Мой
          </span>
        )}
      </div>

      {/* Territory info bar */}
      <div className="flex items-center justify-between px-4 py-2 bg-gray-800/30 border-b border-gray-800">
        <div className="flex items-center gap-3 text-xs">
          <span className="flex items-center gap-1 text-yellow-400">
            <DollarSign className="w-3 h-3" />
            +{territory.passive_income_money}/тик
          </span>
          <span className="flex items-center gap-1 text-blue-400">
            <Globe className="w-3 h-3" />
            +{territory.passive_income_influence}/тик
          </span>
        </div>
        <span className="text-xs text-gray-400">
          🌐 Нужно: {territory.influence_required}
        </span>
      </div>

      {/* District map area with mission circles */}
      <div className="relative w-full mx-auto px-2 py-2 bg-gray-800/30 rounded-xl" style={{ aspectRatio: '4/3', maxHeight: 'calc(100vh - 320px)' }}>
        {/* Territory background pattern */}
        <div
          className="absolute inset-2 rounded-xl opacity-20"
          style={{
            backgroundColor: territory.is_mine ? '#22c55e' : territory.boss?.color || '#4b5563',
          }}
        />

        {/* Grid lines */}
        <svg className="absolute inset-0 w-full h-full" xmlns="http://www.w3.org/2000/svg">
          {[0, 1, 2, 3, 4].map((i) => (
            <React.Fragment key={`grid-${i}`}>
              <line
                x1={`${i * 25}%`} y1="0"
                x2={`${i * 25}%`} y2="100%"
                stroke="#374151" strokeWidth="0.5" opacity="0.3"
              />
              <line
                x1="0" y1={`${i * 25}%`}
                x2="100%" y2={`${i * 25}%`}
                stroke="#374151" strokeWidth="0.5" opacity="0.3"
              />
            </React.Fragment>
          ))}
        </svg>

        {/* Mission circles */}
        {districtMissions.length > 0 ? (
          districtMissions.map((mission: any, idx: number) => {
            // Use position_x/position_y or fall back to predefined positions
            const x = mission.position_x ?? [20, 50, 80, 35, 65][idx % 5];
            const y = mission.position_y ?? [25, 40, 60, 75, 50][idx % 5];
            const color = getMissionColor(mission);

            return (
              <motion.button
                key={mission.id}
                className="absolute transform -translate-x-1/2 -translate-y-1/2 group"
                style={{ left: `${x}%`, top: `${y}%` }}
                onClick={() => handleStartMission(mission)}
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.95 }}
                initial={{ opacity: 0, scale: 0 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: idx * 0.1, duration: 0.3 }}
              >
                {/* Pulse animation for flash missions */}
                {mission.mission_type === 'flash' && (
                  <motion.span
                    className="absolute inset-0 rounded-full"
                    style={{
                      width: 48, height: 48, margin: -10,
                      backgroundColor: color + '40',
                    }}
                    animate={{
                      scale: [1, 1.5, 1],
                      opacity: [0.6, 0, 0.6],
                    }}
                    transition={{
                      duration: 2,
                      repeat: Infinity,
                      ease: 'easeInOut',
                    }}
                  />
                )}

                {/* Mission circle */}
                <motion.div
                  className="relative w-7 h-7 rounded-full border-2 flex items-center justify-center shadow-lg"
                  style={{
                    backgroundColor: color + 'cc',
                    borderColor: color,
                  }}
                  animate={mission.mission_type === 'flash' ? {
                    boxShadow: [
                      `0 0 5px ${color}`,
                      `0 0 20px ${color}`,
                      `0 0 5px ${color}`,
                    ],
                  } : {}}
                  transition={{ duration: 1.5, repeat: Infinity }}
                >
                  <Sword className="w-3.5 h-3.5 text-white" />
                </motion.div>

                {/* Reward label */}
                <div
                  className="absolute top-full left-1/2 -translate-x-1/2 mt-1 px-1.5 py-0.5 rounded text-[9px] font-bold whitespace-nowrap"
                  style={{ backgroundColor: color + 'cc', color: 'white' }}
                >
                  💰{mission.reward_money}
                </div>
              </motion.button>
            );
          })
        ) : (
          <div className="absolute inset-0 flex flex-col items-center justify-center text-gray-500">
            <Target className="w-12 h-12 mb-2 opacity-50" />
            <p className="text-sm">Нет активных миссий</p>
            <p className="text-xs text-gray-600">Миссии появляются автоматически</p>
          </div>
        )}
      </div>

      {/* Requirements panel */}
      <div className="px-4 py-3 bg-gray-800/50 border-t border-gray-800">
        <h3 className="text-xs font-semibold text-gray-400 mb-2">Требования для захвата</h3>
        <div className="grid grid-cols-4 gap-2">
          <div className="bg-gray-900 rounded p-2 text-center">
            <div className="text-sm font-bold text-red-400">💪 {territory.power_required}</div>
            <div className="text-[10px] text-gray-500">Сила</div>
          </div>
          <div className="bg-gray-900 rounded p-2 text-center">
            <div className="text-sm font-bold text-blue-400">🧠 {territory.intellect_required}</div>
            <div className="text-[10px] text-gray-500">Интеллект</div>
          </div>
          <div className="bg-gray-900 rounded p-2 text-center">
            <div className="text-sm font-bold text-green-400">⚡ {territory.agility_required}</div>
            <div className="text-[10px] text-gray-500">Ловкость</div>
          </div>
          <div className="bg-gray-900 rounded p-2 text-center">
            <div className="text-sm font-bold text-purple-400">🌐 {territory.influence_required}</div>
            <div className="text-[10px] text-gray-500">Влияние</div>
          </div>
        </div>

        {/* Capture button (if not mine and can attempt) */}
        {!territory.is_mine && territory.boss && (
          <button
            className="w-full mt-3 py-3 bg-red-600 hover:bg-red-500 text-white font-bold rounded-lg flex items-center justify-center gap-2"
            onClick={() => {
              // TODO: open capture flow
              alert(`Захват: ${territory.name}`);
            }}
          >
            <Sword className="w-5 h-5" />
            Захватить район
          </button>
        )}
        {!territory.is_mine && !territory.boss && (
          <div className="w-full mt-3 py-3 bg-gray-800 text-gray-500 font-bold rounded-lg flex items-center justify-center gap-2 cursor-not-allowed">
            <Lock className="w-4 h-4" />
            Нужно 🌐 {territory.influence_required} влияния
          </div>
        )}
      </div>

      <BottomNav />
    </div>
  );
};
