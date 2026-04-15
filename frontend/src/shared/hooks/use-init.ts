import { useEffect, useState } from 'react';
import { initTelegram, applyTelegramTheme } from '../lib/telegram/telegram';

/**
 * Hook to initialize Telegram WebApp
 */
export function useInit() {
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    const init = () => {
      initTelegram();
      applyTelegramTheme();
      setIsReady(true);
    };

    init();
  }, []);

  return isReady;
}
