export interface UserResources {
  money: number;
  influence: number;
  wanted_level: number;
  active_playtime_minutes: number;
  last_income_tick: string;
}

export interface Mission {
  id: number;
  mission_id: number | null;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  available_until: string | null;
  location_name: string;
  position_x: number;
  position_y: number;
  ends_at: string | null;
  reward_money: number | null;
  template_name: string;
  template_description: string;
  difficulty: string;
}

export interface Territory {
  id: number;
  name: string;
  territory_type: string;
  passive_income_money: number;
  captured_at: string;
}

export interface ShopItem {
  id: number;
  name: string;
  description: string;
  item_type: 'character' | 'weapon' | 'tool';
  cost_money: number;
  cost_influence: number;
  base_power: number | null;
  bonus_power: number | null;
}

export interface DashboardResponse {
  user_id: number;
  telegram_id: number;
  username: string | null;
  resources: UserResources;
  available_missions: Mission[];
  active_missions: Mission[];
  territories: Territory[];
  shop: ShopItem[];
}

declare global {
  interface Window {
    Telegram?: {
      WebApp: {
        initData: string;
        ready: () => void;
        expand: () => void;
        themeParams: Record<string, string>;
        HeaderColor: string;
        BackgroundColor: string;
      };
    };
  }
}
