import { api } from '../../../shared/api/base-api';
import type { Character } from '../model/types';

export const characterApi = {
  getAll: () => api.get<Character[]>('/characters/'),
  getById: (id: number) => api.get<Character>(`/characters/${id}/`),
  equip: (characterId: number, equipmentId: number) =>
    api.post(`/characters/${characterId}/equip/`, { equipment_id: equipmentId }),
};
