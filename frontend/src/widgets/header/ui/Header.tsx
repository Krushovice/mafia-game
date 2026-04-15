import React from 'react';
import { useUserStore } from '../../../entities/user/model/store';

export const Header: React.FC = () => {
  const user = useUserStore((state) => state.user);

  return (
    <header className="mb-6 flex items-center justify-between">
      <h1 className="text-2xl font-bold">🎮 Mafia</h1>
      <span className="text-sm text-gray-400">
        @{user?.username || 'Boss'}
      </span>
    </header>
  );
};
