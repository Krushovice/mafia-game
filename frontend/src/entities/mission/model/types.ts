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

export interface ActiveMission extends Mission {
  current_event_log_id?: number;
  progress?: number;
}

export interface ActiveEvent {
  event_log_id: number;
  event_type: string;
  event_description: string;
  choices: MissionEventChoice[];
}

export interface MissionEvent {
  id: number;
  event_type: string;
  label: string;
  description: string;
  choices: MissionEventChoice[];
}

export interface MissionEventChoice {
  id: number;
  choice_type: string;
  label: string;
  description: string;
  influence_required: number;
  power_required: number;
  money_cost: number;
  success_chance_base: number;
}
