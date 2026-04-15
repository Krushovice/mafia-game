import React from 'react';
import { Card } from '../../../shared/ui/card/Card';
import type { Mission } from '../../../entities/mission/model/types';

interface MissionCardProps {
  mission: Mission;
  onStart?: (missionId: number) => void;
  isActive?: boolean;
}

export const MissionCard: React.FC<MissionCardProps> = ({ mission, onStart, isActive }) => {
  const hasTimer = mission.available_until;

  return (
    <Card>
      <div className="flex justify-between items-start mb-1">
        <span className="font-bold text-lg">{mission.location_name}</span>
        {hasTimer && (
          <span className="text-xs bg-red-900 text-red-200 px-2 py-0.5 rounded">
            ⏳ {new Date(mission.available_until!).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </span>
        )}
      </div>
      <div className="text-sm text-gray-300 mb-2">
        {mission.template_name}
      </div>
      <div className="flex justify-between items-center text-sm">
        <span className="text-yellow-400">💰 {mission.reward_money}</span>
        <span className="text-gray-400 capitalize">{mission.difficulty}</span>
      </div>
      {onStart && !isActive && (
        <button
          className="mt-3 w-full bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-lg transition-colors"
          onClick={() => onStart(mission.id)}
        >
          Начать миссию
        </button>
      )}
    </Card>
  );
};
