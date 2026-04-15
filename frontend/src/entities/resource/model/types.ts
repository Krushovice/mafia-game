export interface Resource {
  money: number;
  influence: number;
  wanted_level: number;
}

export interface ResourceChange {
  money?: number;
  influence?: number;
  wanted_level?: number;
}
