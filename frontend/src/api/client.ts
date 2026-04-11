import type { DashboardResponse } from '../types';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

async function fetchWithAuth(endpoint: string, options: RequestInit = {}) {
  const initData = window.Telegram?.WebApp.initData || '';

  const headers = new Headers(options.headers || {});
  headers.set('Content-Type', 'application/json');
  if (initData) {
    headers.set('X-Telegram-InitData', initData);
  }

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || 'Request failed');
  }

  return response.json();
}

export const api = {
  getDashboard: (): Promise<DashboardResponse> =>
    fetchWithAuth('/tma/dashboard'),

  startMission: (missionId: number, characterIds: number[]) =>
    fetchWithAuth(`/missions/${missionId}/start`, {
      method: 'POST',
      body: JSON.stringify({ character_ids: characterIds }),
    }),

  buyItem: (itemId: number, characterId?: number) =>
    fetchWithAuth('/shop/buy', {
      method: 'POST',
      body: JSON.stringify({ item_id: itemId, character_id: characterId }),
    }),
};
