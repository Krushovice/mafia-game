import type { DashboardResponse, UserResources, Mission, Territory, ShopItem } from '../../types';

export type { DashboardResponse, UserResources, Mission, Territory, ShopItem };

// Global window type extension
declare global {
  interface Window {
    Telegram?: {
      WebApp: {
        initData: string;
        initDataUnsafe: {
          user?: {
            id: number;
            first_name: string;
            last_name?: string;
            username?: string;
            language_code?: string;
            is_premium?: boolean;
          };
          query_id?: string;
          auth_date: number;
          hash: string;
        };
        ready: () => void;
        expand: () => void;
        close: () => void;
        themeParams: Record<string, string>;
        HeaderColor: string;
        BackgroundColor: string;
        MainButton: {
          setText: (text: string) => void;
          setParams: (params: { text: string; is_active?: boolean; is_visible?: boolean }) => void;
          show: () => void;
          hide: () => void;
          enable: () => void;
          disable: () => void;
          onClick: (callback: () => void) => void;
          offClick: (callback: () => void) => void;
          isVisible: boolean;
          isActive: boolean;
          text: string;
        };
        HapticFeedback: {
          impactOccurred: (style: 'light' | 'medium' | 'heavy' | 'rigid' | 'soft') => void;
          notificationOccurred: (type: 'error' | 'success' | 'warning') => void;
          selectionChanged: () => void;
        };
        enableClosingConfirmation: () => void;
        disableClosingConfirmation: () => void;
        onEvent: (eventName: string, callback: () => void) => void;
        offEvent: (eventName: string, callback: () => void) => void;
        showAlert: (message: string, callback?: () => void) => void;
        showConfirm: (message: string, callback: (confirmed: boolean) => void) => void;
      };
    };
  }
}
