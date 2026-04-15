import { useState, useCallback } from 'react';
import { shopApi } from '../../../shared/api/base-api';

export function useBuyItem() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const buyItem = useCallback(async (itemId: number, characterId?: number) => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await shopApi.buyItem(itemId, characterId);
      return result;
    } catch (e) {
      const message = e instanceof Error ? e.message : 'Failed to buy item';
      setError(message);
      throw e;
    } finally {
      setIsLoading(false);
    }
  }, []);

  return { buyItem, isLoading, error };
}
