import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { ROUTES } from '../../../shared/config/routes';
import { useTelegramNative } from '../../../shared/hooks/use-telegram-native';

const TABS = [
  { path: ROUTES.DASHBOARD, label: 'Карта', icon: '🗺️' },
  { path: ROUTES.SHOP, label: 'Магазин', icon: '🏪' },
  { path: ROUTES.CHARACTERS, label: 'Бойцы', icon: '👤' },
  { path: ROUTES.HELP, label: 'Помощь', icon: '❓' },
];

export const BottomNav: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { hapticLight } = useTelegramNative();

  const handleNav = (path: string) => {
    hapticLight();
    navigate(path);
  };

  return (
    <nav 
      className="fixed bottom-0 left-0 right-0 z-50 bg-gray-900 border-t border-gray-800"
      style={{ paddingBottom: 'var(--safe-area-inset-bottom, 0px)' }}
    >
      <div className="flex justify-around items-center max-w-lg mx-auto">
        {TABS.map((tab) => {
          const isActive = location.pathname === tab.path;
          return (
            <button
              key={tab.path}
              className={`flex flex-col items-center py-2 px-3 min-w-[64px] transition-colors ${
                isActive
                  ? 'text-blue-400 bg-gray-800'
                  : 'text-gray-500 active:text-gray-300'
              }`}
              onClick={() => handleNav(tab.path)}
            >
              <span className="text-xl mb-0.5">{tab.icon}</span>
              <span className="text-xs">{tab.label}</span>
            </button>
          );
        })}
      </div>
    </nav>
  );
};
