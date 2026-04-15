import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { missionApi } from '../../../entities/mission/api/mission-api';
import { Header } from '../../../widgets/header/ui/Header';
import { ResourceBar } from '../../../widgets/resource-bar/ui/ResourceBar';
import { Button } from '../../../shared/ui/button/Button';
import { useMissionChoice } from '../../../features/mission-choice/model/use-mission-choice';
import type { MissionEventChoice, ActiveEvent } from '../../../entities/mission/model/types';
import { ROUTES } from '../../../shared/config/routes';

export const MissionActivePage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [currentEvent, setCurrentEvent] = useState<ActiveEvent | null>(null);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const { respondToEvent, isLoading: isResponding } = useMissionChoice();

  const { data: activeMissions, isLoading } = useQuery({
    queryKey: ['active-missions'],
    queryFn: missionApi.getActive,
  });

  const mission = activeMissions?.find((m) => m.id === Number(id));

  // Poll backend for active events
  const { data: backendEvent } = useQuery({
    queryKey: ['active-event', id],
    queryFn: () => (id ? missionApi.getActiveEvent(Number(id)) : Promise.resolve(null)),
    enabled: !!id && !!mission,
    refetchInterval: 3000, // Poll every 3 seconds
  });

  // Update currentEvent when backend event is received
  useEffect(() => {
    if (backendEvent && !currentEvent) {
      setCurrentEvent(backendEvent);
    }
  }, [backendEvent, currentEvent]);

  // Clear poll on unmount
  useEffect(() => {
    return () => {
      if (pollRef.current) clearInterval(pollRef.current);
    };
  }, []);

  const handleChoice = async (choice: MissionEventChoice) => {
    if (!currentEvent || !mission) return;
    await respondToEvent(mission.id, choice.choice_type);
    setCurrentEvent(null);
    // Invalidate the active event query to fetch the next event
    queryClient.invalidateQueries({ queryKey: ['active-event', id] });
    queryClient.invalidateQueries({ queryKey: ['active-missions'] });
  };

  if (isLoading) {
    return <div className="text-center mt-10 text-gray-400">Загрузка...</div>;
  }

  if (!mission) {
    return (
      <div className="text-center mt-10">
        <p className="text-gray-400 mb-4">Миссия не найдена</p>
        <Button onClick={() => navigate(ROUTES.DASHBOARD)}>
          На главную
        </Button>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white p-4 font-sans">
      <Header />
      <ResourceBar />

      {/* Mission Progress */}
      <section className="mb-6">
        <h2 className="text-xl font-bold mb-3">🎯 {mission.location_name}</h2>
        <div className="bg-gray-800 p-4 rounded-lg mb-4">
          <div className="flex justify-between items-center mb-2">
            <span className="text-gray-300">Прогресс</span>
            <span className="text-sm text-gray-400">
              {mission.ends_at
                ? `${Math.max(0, Math.ceil((new Date(mission.ends_at).getTime() - Date.now()) / 60000))} мин`
                : 'В процессе'}
            </span>
          </div>
          <div className="w-full bg-gray-700 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all"
              style={{ width: `${mission.progress || 50}%` }}
            />
          </div>
        </div>
      </section>

      {/* Event Modal */}
      {currentEvent && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-75 p-4">
          <div className="bg-gray-900 rounded-lg border border-yellow-600 max-w-md w-full p-6">
            <h3 className="text-2xl font-bold mb-2">{currentEvent.event_type}</h3>
            <p className="text-gray-300 mb-4">{currentEvent.event_description}</p>
            <div className="space-y-2">
              {currentEvent.choices.map((choice) => (
                <Button
                  key={choice.id}
                  variant="secondary"
                  isLoading={isResponding}
                  onClick={() => handleChoice(choice)}
                  className="w-full text-left"
                >
                  <div>
                    <div className="font-bold">{choice.label}</div>
                    <div className="text-xs text-gray-400">
                      {choice.description}
                      {choice.money_cost > 0 && ` • -${choice.money_cost}💰`}
                      {choice.success_chance_base > 0 &&
                        ` • ${choice.success_chance_base}% шанс`}
                    </div>
                  </div>
                </Button>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Complete Button */}
      <Button
        variant="primary"
        size="lg"
        className="w-full"
        onClick={() => navigate(ROUTES.DASHBOARD)}
      >
        Завершить миссию
      </Button>
    </div>
  );
};
