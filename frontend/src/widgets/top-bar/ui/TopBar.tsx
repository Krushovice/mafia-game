import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useUserStore } from '../../../entities/user/model/store';
import { ROUTES } from '../../../shared/config/routes';

export const TopBar: React.FC = () => {
  const user = useUserStore((state) => state.user);
  const navigate = useNavigate();

  if (!user) return null;

  const { money, influence, wanted_level } = user.resources;

  return (
    <header className="sticky top-0 z-40 bg-gray-900/95 backdrop-blur-sm border-b border-gray-800 px-4 py-2">
      <div className="flex items-center justify-between max-w-lg mx-auto">
        <span className="text-sm font-bold text-white">🎮 Mafia</span>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1">
            <span className="text-yellow-400">💰</span>
            <span className="text-sm font-semibold text-yellow-400">{money}</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="text-blue-400">🌐</span>
            <span className="text-sm font-semibold text-blue-400">{influence}</span>
          </div>
          <button
            className={`flex items-center gap-1 px-2 py-1 rounded ${
              wanted_level > 80
                ? 'bg-red-900 text-red-300'
                : wanted_level > 50
                ? 'bg-orange-900 text-orange-300'
                : 'bg-gray-800 text-gray-400'
            }`}
            onClick={() => navigate(ROUTES.WANTED)}
          >
            <span>⚠️</span>
            <span className="text-sm font-semibold">{wanted_level}</span>
          </button>
        </div>
      </div>
    </header>
  );
};
