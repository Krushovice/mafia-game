import { api, territoriesApi } from '../../../shared/api/base-api';

export const territoryApi = {
  getAll: territoriesApi.getTerritories,
  capture: territoriesApi.captureTerritory,
  getPassiveIncome: () => api.get('/territories/income/'),
};
