import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ROUTES } from '../../shared/config/routes';
import { MapPage } from '../../pages/map/ui/MapPage';
import { MissionsPage } from '../../pages/missions';
import { MissionActivePage } from '../../pages/mission-active';
import { CharactersPage } from '../../pages/characters';
import { ShopPage } from '../../pages/shop';
import { TerritoriesPage } from '../../pages/territories';
import { WantedPage } from '../../pages/wanted';
import { HelpPage } from '../../pages/help';
import { DistrictPage } from '../../pages/district';
import { BottomNav } from '../../widgets/bottom-nav/ui/BottomNav';
import { TopBar } from '../../widgets/top-bar/ui/TopBar';
import { ToastContainer } from '../../shared/ui/toast';

const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <div className="pb-16">
      <TopBar />
      {children}
      <BottomNav />
      <ToastContainer />
    </div>
  );
};

export const RouterProvider: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path={ROUTES.DASHBOARD} element={<MapPage />} />
        <Route path={ROUTES.MISSIONS} element={<Layout><MissionsPage /></Layout>} />
        <Route path={ROUTES.MISSION_ACTIVE} element={<MissionActivePage />} />
        <Route path={ROUTES.CHARACTERS} element={<Layout><CharactersPage /></Layout>} />
        <Route path={ROUTES.SHOP} element={<Layout><ShopPage /></Layout>} />
        <Route path={ROUTES.DISTRICT} element={<DistrictPage />} />
        <Route path={ROUTES.TERRITORIES} element={<Layout><TerritoriesPage /></Layout>} />
        <Route path={ROUTES.WANTED} element={<WantedPage />} />
        <Route path={ROUTES.HELP} element={<Layout><HelpPage /></Layout>} />
        <Route path="*" element={<Navigate to={ROUTES.DASHBOARD} replace />} />
      </Routes>
    </BrowserRouter>
  );
};
