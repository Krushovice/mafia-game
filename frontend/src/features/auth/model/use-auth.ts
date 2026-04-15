import { useState, useCallback } from 'react';
import { dashboardApi } from '../../../shared/api/base-api';
import { useUserStore } from '../../../entities/user/model/store';

export function useAuth() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const setUser = useUserStore((state) => state.setUser);

  const initialize = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const dashboard = await dashboardApi.getDashboard();
      setUser({
        id: dashboard.user_id,
        telegram_id: dashboard.telegram_id,
        username: dashboard.username,
        resources: dashboard.resources,
      });
      return dashboard;
    } catch (e) {
      const message = e instanceof Error ? e.message : 'Failed to initialize';
      setError(message);
      throw e;
    } finally {
      setIsLoading(false);
    }
  }, [setUser]);

  return { isLoading, error, initialize };
}
