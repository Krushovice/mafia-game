import { useState, useCallback } from 'react';
import { missionApi } from '../../../entities/mission/api/mission-api';

export function useStartMission() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const startMission = useCallback(async (missionId: number, characterIds: number[]) => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await missionApi.start(missionId, characterIds);
      return result;
    } catch (e) {
      const message = e instanceof Error ? e.message : 'Failed to start mission';
      setError(message);
      throw e;
    } finally {
      setIsLoading(false);
    }
  }, []);

  return { startMission, isLoading, error };
}
