import { api } from '../../../shared/api/base-api';
import type { MapResponse } from '../model/types';

export const mapApi = {
  getMap: () => api.get<MapResponse>('/map/'),
};
