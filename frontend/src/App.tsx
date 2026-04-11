import { useState, useEffect } from 'react';

declare global {
  interface Window {
    Telegram?: {
      WebApp: {
        initData: string;
        ready: () => void;
        expand: () => void;
        themeParams: Record<string, string>;
      };
    };
  }
}

function App() {
  const [isTelegram, setIsTelegram] = useState(false);
  const [initData, setInitData] = useState('');

  useEffect(() => {
    if (window.Telegram?.WebApp) {
      setIsTelegram(true);
      setInitData(window.Telegram.WebApp.initData);
      window.Telegram.WebApp.ready();
      window.Telegram.WebApp.expand();
    }
  }, []);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-4">
      <h1 className="text-2xl font-bold mb-4">🎮 Mafia Game TMA</h1>
      {isTelegram ? (
        <div className="bg-gray-800 p-4 rounded-lg">
          <p className="text-green-400">✅ Запущено в Telegram</p>
          <p className="text-xs text-gray-400 mt-2 truncate max-w-xs">
            InitData: {initData.substring(0, 50)}...
          </p>
        </div>
      ) : (
        <div className="bg-yellow-800 p-4 rounded-lg">
          <p>⚠️ Запущено вне Telegram</p>
        </div>
      )}
    </div>
  );
}

export default App;
