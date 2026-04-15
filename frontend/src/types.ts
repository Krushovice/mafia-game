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
  territory_id: number | null;
  position_x: number;
  position_y: number;
  ends_at: string | null;
  reward_money: number | null;
  reward_influence: number | null;
  template_name: string;
  template_description: string;
  difficulty: string;
  mission_type?: 'regular' | 'flash' | 'territory';
}

export interface Territory {
  id: number;
  name: string;
  description?: string;
  territory_type: string;
  power_required: number;
  intellect_required: number;
  agility_required: number;
  passive_income_money: number;
  passive_income_influence: number;
  influence_cap_bonus: number;
  is_captured: boolean;
  captured_by_user_id: number | null;
  captured_at?: string;
}

export interface ShopItem {
  id: number;
  name: string;
  description: string;
  item_type: 'character' | 'weapon' | 'tool';
  cost_money: number;
  cost_influence: number;
  base_power: number | null;
  base_intellect: number | null;
  base_agility: number | null;
  bonus_power: number | null;
  bonus_intellect: number | null;
  bonus_agility: number | null;
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
