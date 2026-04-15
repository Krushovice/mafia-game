export const ROUTES = {
  DASHBOARD: '/',
  MISSIONS: '/missions',
  MISSION_ACTIVE: '/mission/:id',
  CHARACTERS: '/characters',
  SHOP: '/shop',
  TERRITORIES: '/territories',
  DISTRICT: '/territories/:id',
  WANTED: '/wanted',
  HELP: '/help',
} as const;

export type RouteKey = keyof typeof ROUTES;
export type RoutePath = (typeof ROUTES)[RouteKey];
