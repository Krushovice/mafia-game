import type { DashboardResponse, Territory } from '../../types';

const API_URL = import.meta.env.VITE_API_URL || '';

interface FetchOptions extends Omit<RequestInit, 'headers'> {
  headers?: Record<string, string>;
}

async function request<T>(endpoint: string, options: FetchOptions = {}): Promise<T> {
  const initData = window.Telegram?.WebApp.initData || '';

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  if (initData) {
    headers['X-Telegram-InitData'] = initData;
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
  get: <T>(endpoint: string) => request<T>(endpoint),
  post: <T>(endpoint: string, body?: Record<string, unknown>) =>
    request<T>(endpoint, {
      method: 'POST',
      body: body ? JSON.stringify(body) : undefined,
    }),
  delete: <T>(endpoint: string) =>
    request<T>(endpoint, { method: 'DELETE' }),
};

// Typed API methods for specific endpoints
export const dashboardApi = {
  getDashboard: () => api.get<DashboardResponse>('/tma/dashboard'),
};

export const missionsApi = {
  startMission: (missionId: number, characterIds: number[]) =>
    api.post(`/missions/${missionId}/start/`, { character_ids: characterIds }),
  completeMission: (userMissionId: number) =>
    api.post(`/user_missions/${userMissionId}/complete/`),
  respondToEvent: (eventLogId: number, choiceType: string) =>
    api.post(`/user_missions/${eventLogId}/respond_event`, { choice_type: choiceType }),
};

export const shopApi = {
  buyItem: (itemId: number, characterId?: number) =>
    api.post('/shop/buy/', { item_id: itemId, character_id: characterId }),
};

export const territoriesApi = {
  getTerritories: () => api.get<Territory[]>('/territories/'),
  captureTerritory: (territoryId: number) =>
    api.post(`/territories/${territoryId}/capture/`),
};

export const wantedApi = {
  getStatus: () => api.get('/wanted/status'),
  applyCooldown: () => api.post('/wanted/cooldown'),
};
