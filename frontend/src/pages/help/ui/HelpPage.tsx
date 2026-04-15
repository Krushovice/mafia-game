import React from 'react';
import { Header } from '../../../widgets/header/ui/Header';
import { ResourceBar } from '../../../widgets/resource-bar/ui/ResourceBar';
import { BottomNav } from '../../../widgets/bottom-nav/ui/BottomNav';

const FAQ_ITEMS = [
  {
    q: 'Что такое Influence (Влияние)?',
    a: 'Влияние определяет, какие территории ты можешь захватить. Каждая следующая территория требует больше влияния. Захват территорий увеличивает твой максимальный лимит влияния.',
  },
  {
    q: 'Как захватить территорию?',
    a: 'Открой вкладку "Кварталы", выбери свободную территорию и нажми "Захватить". Тебе нужно достаточно влияния и 3 свободных бойца для миссии захвата.',
  },
  {
    q: 'Что такое Wanted Level (Розыск)?',
    a: 'Уровень розыск растёт с каждой миссией. При высоком уровне миссии становятся сложнее. Дождись снижения или используй cooldown.',
  },
  {
    q: 'Как работает пассивный доход?',
    a: 'Каждая захваченная территория приносит монеты и влияние каждые 10 минут. Доход увеличивается с количеством территорий.',
  },
  {
    q: 'Какие типы миссий бывают?',
    a: 'Обычные (regular) — стандартные миссии на карте. Flash (⚡) —限时 миссии с таймером и повышенными наградами. Territory — миссии захвата территорий.',
  },
  {
    q: 'Что такое Flash миссии?',
    a: 'Временные миссии, которые появляются случайно и исчезают через некоторое время. Они дают повышенные награды, но требуют быстрой реакции.',
  },
  {
    q: 'Как улучшить бойцов?',
    a: 'В магазине можно купить оружие и инструменты для бойцов. Экипировка увеличивает их характеристики (Power, Intellect, Agility).',
  },
];

export const HelpPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-900 text-white p-4 font-sans">
      <Header />
      <ResourceBar />

      <div className="mb-6">
        <h1 className="text-2xl font-bold mb-2">❓ Помощь</h1>
        <p className="text-gray-400 text-sm">
          Основы геймплея Mafia TMA
        </p>
      </div>

      {/* FAQ */}
      <section className="space-y-3 mb-20">
        {FAQ_ITEMS.map((item, index) => (
          <div key={index} className="bg-gray-800 rounded-lg p-4">
            <h3 className="font-bold text-white mb-2">{item.q}</h3>
            <p className="text-gray-300 text-sm">{item.a}</p>
          </div>
        ))}
      </section>

      <BottomNav />
    </div>
  );
};
