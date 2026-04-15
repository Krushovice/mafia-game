import React from 'react';
import { QueryProvider } from './providers/query-provider';
import { RouterProvider } from './providers/router-provider';
import { useInit } from '../shared/hooks/use-init';
import { ErrorBoundary } from '../shared/error-boundary';

export const App: React.FC = () => {
  const isReady = useInit();

  if (!isReady) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-gray-400 text-xl">Инициализация...</div>
      </div>
    );
  }

  return (
    <ErrorBoundary>
      <QueryProvider>
        <RouterProvider />
      </QueryProvider>
    </ErrorBoundary>
  );
};
