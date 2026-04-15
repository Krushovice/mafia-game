import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { characterApi } from '../../../entities/character/api/character-api';
import { Header } from '../../../widgets/header/ui/Header';
import { ResourceBar } from '../../../widgets/resource-bar/ui/ResourceBar';
import { Card } from '../../../shared/ui/card/Card';
import type { Character } from '../../../entities/character/model/types';

export const CharactersPage: React.FC = () => {
  const { data: characters, isLoading, error } = useQuery({
    queryKey: ['characters'],
    queryFn: characterApi.getAll,
  });

  if (isLoading) {
    return <div className="text-center mt-10 text-gray-400">Загрузка...</div>;
  }

  if (error) {
    return <div className="text-center mt-10 text-red-500">Ошибка: {(error as Error).message}</div>;
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white p-4 font-sans">
      <Header />
      <ResourceBar />

      <h2 className="text-xl font-bold mb-4">👥 Бойцы</h2>

      <div className="space-y-3">
        {characters?.map((char: Character) => (
          <Card key={char.id}>
            <div className="flex justify-between items-start mb-2">
              <div>
                <h3 className="font-bold text-lg">{char.name}</h3>
                <p className="text-sm text-gray-400 capitalize">{char.role}</p>
              </div>
              <span
                className={`text-xs px-2 py-1 rounded ${
                  char.is_active
                    ? 'bg-green-900 text-green-200'
                    : 'bg-gray-700 text-gray-400'
                }`}
              >
                {char.is_active ? 'Активен' : 'Неактивен'}
              </span>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-3 gap-2 mb-3">
              <div className="text-center">
                <div className="text-2xl">💪</div>
                <div className="text-sm font-bold">{char.power}</div>
                <div className="text-xs text-gray-400">Power</div>
              </div>
              <div className="text-center">
                <div className="text-2xl">🧠</div>
                <div className="text-sm font-bold">{char.intellect}</div>
                <div className="text-xs text-gray-400">Intellect</div>
              </div>
              <div className="text-center">
                <div className="text-2xl">⚡</div>
                <div className="text-sm font-bold">{char.agility}</div>
                <div className="text-xs text-gray-400">Agility</div>
              </div>
            </div>

            {/* Equipment */}
            <div className="text-sm text-gray-400">
              {char.weapon_id && <span>🔫 Оружие ID: {char.weapon_id}</span>}
              {char.tool_id && <span className="ml-2">🔧 Инструмент ID: {char.tool_id}</span>}
              {!char.weapon_id && !char.tool_id && (
                <span>Без экипировки</span>
              )}
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
};
