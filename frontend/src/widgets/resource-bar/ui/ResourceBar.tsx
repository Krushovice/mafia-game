import React from 'react';
import { useUserStore } from '../../../entities/user/model/store';
import { ROUTES } from '../../../shared/config/routes';
import { useNavigate } from 'react-router-dom';

export const ResourceBar: React.FC = () => {
  const user = useUserStore((state) => state.user);
  const navigate = useNavigate();

  if (!user) return null;

  const { money, influence, wanted_level } = user.resources;

  return (
    <section className="grid grid-cols-3 gap-3 mb-6">
      <div className="bg-gray-800 p-3 rounded-lg text-center">
        <div className="text-2xl mb-1">💰</div>
        <div className="text-lg font-bold">{money}</div>
        <div className="text-xs text-gray-400">Coins</div>
      </div>
      <div className="bg-gray-800 p-3 rounded-lg text-center">
        <div className="text-2xl mb-1">🌐</div>
        <div className="text-lg font-bold">{influence}</div>
        <div className="text-xs text-gray-400">Influence</div>
      </div>
      <div
        className="bg-gray-800 p-3 rounded-lg text-center cursor-pointer hover:bg-gray-700 transition-colors"
        onClick={() => navigate(ROUTES.WANTED)}
      >
        <div className="text-2xl mb-1">⚠️</div>
        <div
          className={`text-lg font-bold ${
            wanted_level > 50 ? 'text-red-500' : ''
          }`}
        >
          {wanted_level}
        </div>
        <div className="text-xs text-gray-400">Wanted</div>
      </div>
    </section>
  );
};
