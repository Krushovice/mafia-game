import { create } from 'zustand';
import type { User, UserResources } from './types';

interface UserState {
  user: User | null;
  setUser: (user: User) => void;
  updateResources: (resources: Partial<UserResources>) => void;
}

export const useUserStore = create<UserState>((set) => ({
  user: null,
  setUser: (user) => set({ user }),
  updateResources: (resources) =>
    set((state) => ({
      user: state.user
        ? { ...state.user, resources: { ...state.user.resources, ...resources } }
        : null,
    })),
}));
