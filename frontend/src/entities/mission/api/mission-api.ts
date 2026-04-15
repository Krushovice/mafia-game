import { api, missionsApi } from '../../../shared/api/base-api';
import type { Mission, ActiveMission, ActiveEvent } from '../model/types';

export const missionApi = {
  getAvailable: () => api.get<Mission[]>('/missions/'),
  getActive: () => api.get<ActiveMission[]>('/user_missions/'),
  start: missionsApi.startMission,
  complete: missionsApi.completeMission,
  respondToEvent: missionsApi.respondToEvent,
  getActiveEvent: (missionId: number) =>
    api.get<ActiveEvent>(`/user_missions/${missionId}/active_event`),
};
