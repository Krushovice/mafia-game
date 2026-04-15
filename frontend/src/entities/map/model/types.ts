export interface NPCBoss {
  id: number;
  name: string;
  color: string;
  influence: number;
  power: number;
}

export interface MapTerritory {
  id: number;
  name: string;
  territory_type: string;
  description: string;
  grid_x: number;
  grid_y: number;
  influence_required: number;
  power_required: number;
  intellect_required: number;
  agility_required: number;
  passive_income_money: number;
  passive_income_influence: number;
  reward_influence: number;
  reward_money: number;
  is_mine: boolean;
  boss: NPCBoss | null;
}

export interface MapResponse {
  territories: MapTerritory[];
}
