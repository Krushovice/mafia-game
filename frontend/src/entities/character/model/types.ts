export interface Character {
  id: number;
  name: string;
  role: string;
  power: number;
  intellect: number;
  agility: number;
  weapon_id: number | null;
  tool_id: number | null;
  is_active: boolean;
  is_busy: boolean;
}

export interface CharacterEquipment {
  weapon: EquipmentItem | null;
  tool: EquipmentItem | null;
}

export interface EquipmentItem {
  id: number;
  name: string;
  description: string;
  bonus_power: number | null;
  bonus_intellect: number | null;
  bonus_agility: number | null;
}
