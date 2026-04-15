import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { dashboardApi } from '../../../shared/api/base-api';
import { Header } from '../../../widgets/header/ui/Header';
import { ResourceBar } from '../../../widgets/resource-bar/ui/ResourceBar';
import { Card } from '../../../shared/ui/card/Card';
import { Button } from '../../../shared/ui/button/Button';
import { useBuyItem } from '../../../features/buy-item/model/use-buy-item';
import { showConfirm } from '../../../shared/lib/telegram/telegram';
import type { ShopItem } from '../../../types';

export const ShopPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'character' | 'weapon' | 'tool'>('character');
  const { buyItem, isLoading } = useBuyItem();

  const { data: dashboard, isLoading: isLoadingDashboard } = useQuery({
    queryKey: ['dashboard'],
    queryFn: dashboardApi.getDashboard,
  });

  const shopItems = dashboard?.shop || [];
  const filteredItems = shopItems.filter((item: ShopItem) => item.item_type === activeTab);

  const handleBuy = async (item: ShopItem) => {
    const confirmed = await showConfirm(
      `Купить ${item.name} за ${item.cost_money}💰?`
    );
    if (confirmed) {
      await buyItem(item.id);
    }
  };

  if (isLoadingDashboard) {
    return <div className="text-center mt-10 text-gray-400">Загрузка...</div>;
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white p-4 font-sans">
      <Header />
      <ResourceBar />

      {/* Tabs */}
      <div className="flex gap-2 mb-4">
        <button
          className={`px-4 py-2 rounded-lg ${
            activeTab === 'character'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-800 text-gray-400'
          }`}
          onClick={() => setActiveTab('character')}
        >
          Бойцы
        </button>
        <button
          className={`px-4 py-2 rounded-lg ${
            activeTab === 'weapon'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-800 text-gray-400'
          }`}
          onClick={() => setActiveTab('weapon')}
        >
          Оружие
        </button>
        <button
          className={`px-4 py-2 rounded-lg ${
            activeTab === 'tool'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-800 text-gray-400'
          }`}
          onClick={() => setActiveTab('tool')}
        >
          Инструменты
        </button>
      </div>

      {/* Shop Items */}
      <div className="space-y-3">
        {filteredItems.length > 0 ? (
          filteredItems.map((item: ShopItem) => (
            <Card key={item.id}>
              <div className="flex justify-between items-start mb-2">
                <div>
                  <h3 className="font-bold text-lg">{item.name}</h3>
                  <p className="text-sm text-gray-400">{item.description}</p>
                </div>
                <div className="text-right">
                  <div className="text-yellow-400 font-bold">{item.cost_money}💰</div>
                  {item.cost_influence > 0 && (
                    <div className="text-sm text-gray-400">
                      {item.cost_influence}🌐
                    </div>
                  )}
                </div>
              </div>

              {(item.base_power || item.base_intellect || item.base_agility) && (
                <div className="text-sm text-gray-300 mb-2">
                  {item.base_power && <span>💪 {item.base_power}</span>}
                  {item.base_intellect && <span> | 🧠 {item.base_intellect}</span>}
                  {item.base_agility && <span> | ⚡ {item.base_agility}</span>}
                </div>
              )}

              <Button
                variant="primary"
                size="sm"
                isLoading={isLoading}
                onClick={() => handleBuy(item)}
                className="w-full"
              >
                Купить
              </Button>
            </Card>
          ))
        ) : (
          <p className="text-gray-500 text-center py-4">Нет товаров</p>
        )}
      </div>
    </div>
  );
};
