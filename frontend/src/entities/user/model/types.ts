export interface User {
  id: number;
  telegram_id: number;
  username: string | null;
  resources: UserResources;
}

export interface UserResources {
  money: number;
  influence: number;
  wanted_level: number;
  active_playtime_minutes: number;
  last_income_tick: string;
}
