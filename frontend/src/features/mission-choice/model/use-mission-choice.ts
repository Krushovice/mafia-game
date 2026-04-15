import { useState, useCallback } from 'react';
import { missionApi } from '../../../entities/mission/api/mission-api';

export function useMissionChoice() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const respondToEvent = useCallback(async (missionId: number, choiceType: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await missionApi.respondToEvent(missionId, choiceType);
      return result;
    } catch (e) {
      const message = e instanceof Error ? e.message : 'Failed to respond to event';
      setError(message);
      throw e;
    } finally {
      setIsLoading(false);
    }
  }, []);

  return { respondToEvent, isLoading, error };
}
