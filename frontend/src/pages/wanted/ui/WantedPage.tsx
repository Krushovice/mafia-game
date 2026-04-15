import React from 'react';
import { useUserStore } from '../../../entities/user/model/store';
import { Header } from '../../../widgets/header/ui/Header';
import { ResourceBar } from '../../../widgets/resource-bar/ui/ResourceBar';
import { Card } from '../../../shared/ui/card/Card';
import { Button } from '../../../shared/ui/button/Button';
import { showConfirm } from '../../../shared/lib/telegram/telegram';

export const WantedPage: React.FC = () => {
  const user = useUserStore((state) => state.user);

  if (!user) return null;

  const { wanted_level } = user.resources;
  const isBlocked = wanted_level > 80;
  const progressPercent = Math.min(100, (wanted_level / 100) * 100);

  const handleCooldown = async () => {
    const confirmed = await showConfirm(
      'Снизить уровень розыска? Это займет время.'
    );
    if (confirmed) {
      // await wantedApi.applyCooldown();
      alert('Cooldown applied! (Backend endpoint needed)');
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white p-4 font-sans">
      <Header />
      <ResourceBar />

      <h2 className="text-xl font-bold mb-4">⚠️ Уровень розыска</h2>

      <Card>
        {/* Progress Bar */}
        <div className="mb-4">
          <div className="flex justify-between items-center mb-2">
            <span className="text-lg font-bold">Wanted Level</span>
            <span
              className={`text-2xl font-bold ${
                isBlocked ? 'text-red-500' : 'text-yellow-400'
              }`}
            >
              {wanted_level}
            </span>
          </div>
          <div className="w-full bg-gray-700 rounded-full h-4">
            <div
              className={`h-4 rounded-full transition-all ${
                isBlocked ? 'bg-red-600' : 'bg-yellow-500'
              }`}
              style={{ width: `${progressPercent}%` }}
            />
          </div>
          <div className="text-sm text-gray-400 mt-1">
            {isBlocked
              ? '🚫 Миссии заблокированы!'
              : `${80 - wanted_level} очков до блокировки миссий`}
          </div>
        </div>

        {/* Info */}
        <div className="text-sm text-gray-300 mb-4">
          <p>• Уровень розыска растет после миссий (+2-5 за миссию)</p>
          <p>• При {'>'}80 — новые миссии недоступны</p>
          <p>• Снижается со временем автоматически</p>
        </div>

        {/* Cooldown Button */}
        <Button
          variant="secondary"
          size="lg"
          onClick={handleCooldown}
          disabled={wanted_level === 0}
          className="w-full"
        >
          {wanted_level === 0 ? 'Розыск на нуле' : 'Снизить розыск'}
        </Button>
      </Card>
    </div>
  );
};
