import { useState, useEffect } from 'react';
import { api } from './api/client';
import type { DashboardResponse } from './types';

function App() {
  const [dashboard, setDashboard] = useState<DashboardResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (window.Telegram?.WebApp) {
      window.Telegram.WebApp.ready();
      window.Telegram.WebApp.expand();
    }

    api.getDashboard()
      .then(setDashboard)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading)
    return <div className="text-center mt-10 text-gray-400">Загрузка...</div>;
  if (error)
    return (
      <div className="text-center mt-10 text-red-500">
        Ошибка: {error}
      </div>
    );
  if (!dashboard)
    return (
      <div className="text-center mt-10 text-gray-400">Нет данных</div>
    );

  const { resources, available_missions, territories } = dashboard;

  return (
    <div className="min-h-screen bg-gray-900 text-white p-4 font-sans">
      {/* Header */}
      <header className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold">🎮 Mafia</h1>
        <span className="text-sm text-gray-400">
          @{dashboard.username || 'Boss'}
        </span>
      </header>

      {/* Resources Bar */}
      <section className="grid grid-cols-3 gap-3 mb-6">
        <div className="bg-gray-800 p-3 rounded-lg text-center">
          <div className="text-2xl mb-1">💰</div>
          <div className="text-lg font-bold">{resources.money}</div>
          <div className="text-xs text-gray-400">Coins</div>
        </div>
        <div className="bg-gray-800 p-3 rounded-lg text-center">
          <div className="text-2xl mb-1">🌐</div>
          <div className="text-lg font-bold">{resources.influence}</div>
          <div className="text-xs text-gray-400">Influence</div>
        </div>
        <div className="bg-gray-800 p-3 rounded-lg text-center">
          <div className="text-2xl mb-1">⚠️</div>
          <div
            className={`text-lg font-bold ${
              resources.wanted_level > 50 ? 'text-red-500' : ''
            }`}
          >
            {resources.wanted_level}
          </div>
          <div className="text-xs text-gray-400">Wanted</div>
        </div>
      </section>

      {/* Missions */}
      <section className="mb-6">
        <h2 className="text-xl font-bold mb-3">🗺️ Миссии</h2>
        {available_missions.length > 0 ? (
          <div className="space-y-3">
            {available_missions.map((m) => (
              <div
                key={m.id}
                className="bg-gray-800 p-4 rounded-lg border border-gray-700"
              >
                <div className="flex justify-between items-start mb-1">
                  <span className="font-bold text-lg">{m.location_name}</span>
                  {m.available_until && (
                    <span className="text-xs bg-red-900 text-red-200 px-2 py-0.5 rounded">
                      ⏳ {new Date(m.available_until).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>
                  )}
                </div>
                <div className="text-sm text-gray-300 mb-2">
                  {m.template_name}
                </div>
                <div className="flex justify-between items-center text-sm">
                  <span className="text-yellow-400">💰 {m.reward_money}</span>
                  <span className="text-gray-400 capitalize">
                    {m.difficulty}
                  </span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500 text-center py-4">Нет доступных миссий</p>
        )}
      </section>

      {/* Territories */}
      <section>
        <h2 className="text-xl font-bold mb-3">🏘️ Территории</h2>
        <div className="bg-gray-800 p-4 rounded-lg">
          <div className="flex justify-between items-center mb-2">
            <span className="text-gray-300">Захвачено:</span>
            <span className="font-bold">{territories.length}</span>
          </div>
          {territories.length > 0 && (
            <div className="text-sm text-gray-400">
              Доход: +{territories.reduce((sum, t) => sum + t.passive_income_money, 0)}💰/тик
            </div>
          )}
        </div>
      </section>
    </div>
  );
}

export default App;
