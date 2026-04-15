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
}

export interface UserTerritory {
  id: number;
  territory_id: number;
  captured_at: string;
  territory: Territory;
}
