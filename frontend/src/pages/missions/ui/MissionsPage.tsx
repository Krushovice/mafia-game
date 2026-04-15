import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { dashboardApi } from '../../../shared/api/base-api';
import { characterApi } from '../../../entities/character/api/character-api';
import { Header } from '../../../widgets/header/ui/Header';
import { ResourceBar } from '../../../widgets/resource-bar/ui/ResourceBar';
import { MissionCard } from '../../../widgets/mission-card/ui/MissionCard';
import { useStartMission } from '../../../features/start-mission/model/use-start-mission';
import type { Mission } from '../../../entities/mission/model/types';
import type { Character } from '../../../entities/character/model/types';

export const MissionsPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'regular' | 'flash'>('regular');
  const [selectedMission, setSelectedMission] = useState<Mission | null>(null);
  const [selectedCharId, setSelectedCharId] = useState<number | null>(null);

  const { startMission, isLoading: isStarting } = useStartMission();

  const { data: dashboard, isLoading, error } = useQuery({
    queryKey: ['dashboard'],
    queryFn: dashboardApi.getDashboard,
  });

  const { data: characters } = useQuery({
    queryKey: ['characters'],
    queryFn: characterApi.getAll,
  });

  const missions = dashboard?.available_missions || [];
  const filteredMissions = missions.filter((m: Mission) => {
    if (activeTab === 'flash') {
      return m.mission_type === 'flash';
    }
    return m.mission_type !== 'flash';
  });

  const handleStartMission = async (missionId: number) => {
    const mission = missions.find((m: Mission) => m.id === missionId);
    if (!mission) return;
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
      // Error is handled by the hook
    }
  };

  if (isLoading) {
    return <div className="text-center mt-10 text-gray-400">Загрузка...</div>;
  }

  if (error) {
    return <div className="text-center mt-10 text-red-500">Ошибка: {(error as Error).message}</div>;
  }

  // Character selection modal
  if (selectedMission) {
    const chars = characters || [];
    return (
      <div className="min-h-screen bg-gray-900 text-white p-4 font-sans">
        <Header />
        <ResourceBar />

        <div className="fixed inset-0 z-50 bg-black/80 flex items-end sm:items-center justify-center p-0 sm:p-4">
          <div className="bg-gray-900 rounded-t-2xl sm:rounded-2xl border border-gray-800 w-full sm:max-w-md max-h-[90vh] overflow-y-auto">
            <div className="p-4 border-b border-gray-800">
              <div className="font-bold text-white mb-1">{selectedMission.location_name}</div>
              <div className="text-sm text-gray-400">
                💰 {selectedMission.reward_money} | 🌐 {selectedMission.reward_influence} | {selectedMission.difficulty}
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

  return (
    <div className="min-h-screen bg-gray-900 text-white p-4 font-sans">
      <Header />
      <ResourceBar />

      {/* Tabs */}
      <div className="flex gap-2 mb-4">
        <button
          className={`px-4 py-2 rounded-lg ${
            activeTab === 'regular'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-800 text-gray-400'
          }`}
          onClick={() => setActiveTab('regular')}
        >
          Обычные
        </button>
        <button
          className={`px-4 py-2 rounded-lg ${
            activeTab === 'flash'
              ? 'bg-red-600 text-white'
              : 'bg-gray-800 text-gray-400'
          }`}
          onClick={() => setActiveTab('flash')}
        >
          ⚡ Flash
        </button>
      </div>

      {/* Mission List */}
      <section className="space-y-3">
        {filteredMissions.length > 0 ? (
          filteredMissions.map((m: Mission) => (
            <MissionCard key={m.id} mission={m} onStart={handleStartMission} />
          ))
        ) : (
          <p className="text-gray-500 text-center py-4">
            {activeTab === 'flash'
              ? 'Нет всплывающих миссий'
              : 'Нет доступных миссий'}
          </p>
        )}
      </section>
    </div>
  );
};
