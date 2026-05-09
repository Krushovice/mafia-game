import React, { useState } from 'react';
import { motion } from 'framer-motion';
import type { MapTerritory } from '../frontend/src/entities/map/model/types';
import { useTelegramNative } from '../frontend/src/shared/hooks/use-telegram-native';

interface CityMapProps {
  territories: MapTerritory[];
  onTerritoryClick: (territory: MapTerritory) => void;
}

/**
 * SVG polygon paths для 6 территорий, формирующих островной город.
 * Координаты спроектированы для viewBox="0 0 800 600".
 * Каждый полигон — это отдельная зона с органическими формами и водными разрывами между ними.
 * На основе оригинальной карты города:
 * - ЦЕНТР (yellow) - верхний левый угол, небоскрёбы
 * - ИНДУСТРИАЛЬНАЯ ЗОНА (gray/black) - верхний правый угол, заводы
 * - ЖИЛОЙ РАЙОН (green) - правая сторона, дома с деревьями
 * - ПРИГОРОДЬ (blue) - центр, контейнеры
 * - ПОРТ (purple) - нижняя часть, ящики и грузы
 * - КИТАЙСКИЙ КВАРТАЛ (red/orange) - левая сторона, традиционные здания
 */
const TERRITORY_PATHS: Record<number, string> = {
  // 1. ЦЕНТР — верхний левый угол, жёлтый, небоскрёбы
  1: 'M 70,65 L 180,45 L 280,60 L 300,110 L 260,160 L 180,150 L 90,140 L 40,100 Z',
  // 2. ИНДУСТРИАЛЬНАЯ ЗОНА — верхний правый угол, серый/чёрный, заводы
  2: 'M 380,60 L 760,55 L 790,110 L 780,180 L 740,240 L 680,260 L 600,240 L 520,200 L 430,160 L 380,90 Z',
  // 3. ЖИЛОЙ РАЙОН — правая сторона, зелёный, дома с деревьями
  3: 'M 600,240 L 790,250 L 800,320 L 780,400 L 740,480 L 680,510 L 600,500 L 520,460 L 480,420 L 430,380 L 400,320 L 450,270 L 520,240 Z',
  // 4. ПРИГОРОДЬ — центр, синий, контейнеры
  4: 'M 180,150 L 360,140 L 420,190 L 400,270 L 340,330 L 240,340 L 160,300 L 120,240 L 150,180 Z',
  // 5. ПОРТ — нижняя часть, фиолетовый, ящики и грузы
  5: 'M 120,340 L 240,360 L 340,390 L 480,420 L 520,460 L 480,520 L 400,540 L 320,530 L 240,510 L 160,490 Z',
  // 6. КИТАЙСКИЙ КВАРТАЛ — левая сторона, красный/оранжевый, традиционные здания
  6: 'M 40,100 L 180,120 L 200,170 L 190,230 L 150,290 L 100,330 L 80,280 L 60,220 Z',
};

/**
 * Get the fill color for a territory based on ownership.
 */
function getTerritoryFill(t: MapTerritory): string {
  if (t.is_mine) return '#22c55e'; // Зелёный — мой
  if (t.boss) return t.boss.color; // Цвет босса — NPC
  return '#4b5563'; // Серый — свободный
}

/**
 * Get a lighter stroke/border color.
 */
function getTerritoryStroke(t: MapTerritory): string {
  if (t.is_mine) return '#4ade80';
  if (t.boss) return t.boss.color;
  return '#6b7280';
}

/**
 * CityMap — SVG карта города с цветными полигонами кварталов.
 * Каждый полигон кликабельный, цвет зависит от владельца.
 */
export const CityMap: React.FC<CityMapProps> = ({ territories, onTerritoryClick }) => {
  const [hoveredId, setHoveredId] = useState<number | null>(null);
  const { hapticLight } = useTelegramNative();

  // Animation variants for territory polygons
  const territoryVariants = {
    hidden: { opacity: 0, scale: 0.8 },
    visible: (i: number) => ({
      opacity: 1,
      scale: 1,
      transition: {
        delay: i * 0.1,
        duration: 0.4,
        ease: 'easeOut' as const,
      },
    }),
    hover: {
      scale: 1.02,
      transition: { duration: 0.2 },
    },
  };

  if (!territories.length) {
    return (
      <div className="flex items-center justify-center h-full text-gray-500">
        Карта загружается...
      </div>
    );
  }

  const handleTerritoryClick = (t: MapTerritory) => {
    hapticLight();
    onTerritoryClick(t);
  };

  return (
    <svg
      viewBox="0 0 800 600"
      className="w-full h-full"
      xmlns="http://www.w3.org/2000/svg"
    >
      {/*defs — фильтры и градиенты */}
      <defs>
        {/* Water pattern */}
        <radialGradient id="waterGrad" cx="50%" cy="50%" r="60%">
          <stop offset="0%" stopColor="#1e3a5f" />
          <stop offset="100%" stopColor="#0f1f33" />
        </radialGradient>

        {/* Glow filter for selected/hovered territories */}
        <filter id="glow">
          <feGaussianBlur stdDeviation="3" result="coloredBlur" />
          <feMerge>
            <feMergeNode in="coloredBlur" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>

        {/* Shadow for territory labels */}
        <filter id="labelShadow">
          <feDropShadow dx="0" dy="1" stdDeviation="2" floodColor="#000" floodOpacity="0.8" />
        </filter>
      </defs>

      {/* Water background */}
      <rect width="800" height="600" fill="url(#waterGrad)" />

      {/* Subtle water ripple lines */}
      {[50, 100, 150, 200, 250, 300, 350, 400, 450, 500, 550].map((y) => (
        <path
          key={`wave-${y}`}
          d={`M 0,${y} Q 200,${y - 5} 400,${y} Q 600,${y + 5} 800,${y}`}
          fill="none"
          stroke="#1e4976"
          strokeWidth="0.5"
          opacity="0.3"
        />
      ))}

      {/* Island coastline — outer border around all territories */}
      <path
        d="M 25,420 L 30,320 L 30,220 L 40,180 L 190,130 L 190,50 L 320,30 L 440,50 L 480,60 L 580,40 L 700,60 L 760,120 L 760,200 L 740,270 L 720,270 L 740,360 L 700,430 L 720,500 L 700,560 L 600,570 L 500,540 L 480,460 L 220,470 L 180,520 L 100,530 L 50,480 Z"
        fill="none"
        stroke="#8B7355"
        strokeWidth="4"
        strokeLinejoin="round"
        opacity="0.6"
      />
      <path
        d="M 25,420 L 30,320 L 30,220 L 40,180 L 190,130 L 190,50 L 320,30 L 440,50 L 480,60 L 580,40 L 700,60 L 760,120 L 760,200 L 740,270 L 720,270 L 740,360 L 700,430 L 720,500 L 700,560 L 600,570 L 500,540 L 480,460 L 220,470 L 180,520 L 100,530 L 50,480 Z"
        fill="none"
        stroke="#D2B48C"
        strokeWidth="2"
        strokeLinejoin="round"
        opacity="0.4"
      />

      {/* Territory polygons */}
      {territories.map((t, idx) => {
        const path = TERRITORY_PATHS[t.id];
        if (!path) return null;

        const fill = getTerritoryFill(t);
        const stroke = getTerritoryStroke(t);

        return (
          <motion.g
            key={t.id}
            className="cursor-pointer"
            onClick={() => handleTerritoryClick(t)}
            onMouseEnter={() => setHoveredId(t.id)}
            onMouseLeave={() => setHoveredId(null)}
            initial="hidden"
            animate="visible"
            whileHover="hover"
            custom={idx}
            variants={territoryVariants}
          >
            {/* Territory polygon */}
            <motion.path
              d={path}
              fill={fill}
              fillOpacity={hoveredId === t.id ? 0.95 : 0.85}
              stroke={stroke}
              strokeWidth={hoveredId === t.id ? 4 : 2.5}
              strokeLinejoin="round"
              style={{
                filter: t.is_mine ? 'url(#glow)' : hoveredId === t.id ? 'url(#glow)' : undefined,
              }}
            />

            {/* Territory name label */}
            <text
              x={getLabelPosition(t.id).x}
              y={getLabelPosition(t.id).y}
              textAnchor="middle"
              dominantBaseline="middle"
              fill="white"
              fontSize="13"
              fontWeight="bold"
              fontFamily="system-ui, sans-serif"
              filter="url(#labelShadow)"
              style={{ pointerEvents: 'none' }}
            >
              {t.name}
            </text>

            {/* Income label */}
            <text
              x={getLabelPosition(t.id).x}
              y={getLabelPosition(t.id).y + 16}
              textAnchor="middle"
              dominantBaseline="middle"
              fill="#fbbf24"
              fontSize="10"
              fontWeight="600"
              fontFamily="system-ui, sans-serif"
              filter="url(#labelShadow)"
              style={{ pointerEvents: 'none' }}
            >
              💰+{t.passive_income_money}/тик
            </text>

            {/* Boss name badge (if NPC-owned) */}
            {!t.is_mine && t.boss && (
              <g style={{ pointerEvents: 'none' }}>
                <rect
                  x={getLabelPosition(t.id).x - 40}
                  y={getLabelPosition(t.id).y + 28}
                  width="80"
                  height="18"
                  rx="9"
                  fill={t.boss.color}
                  fillOpacity="0.8"
                />
                <text
                  x={getLabelPosition(t.id).x}
                  y={getLabelPosition(t.id).y + 38}
                  textAnchor="middle"
                  dominantBaseline="middle"
                  fill="white"
                  fontSize="9"
                  fontWeight="600"
                  fontFamily="system-ui, sans-serif"
                >
                  {t.boss.name.split(' ').slice(-1)[0]}
                </text>
              </g>
            )}

            {/* "МОЙ" badge for owned territories */}
            {t.is_mine && (
              <g style={{ pointerEvents: 'none' }}>
                <rect
                  x={getLabelPosition(t.id).x - 20}
                  y={getLabelPosition(t.id).y + 28}
                  width="40"
                  height="18"
                  rx="9"
                  fill="#22c55e"
                  fillOpacity="0.9"
                />
                <text
                  x={getLabelPosition(t.id).x}
                  y={getLabelPosition(t.id).y + 38}
                  textAnchor="middle"
                  dominantBaseline="middle"
                  fill="white"
                  fontSize="9"
                  fontWeight="bold"
                  fontFamily="system-ui, sans-serif"
                >
                  МОЙ
                </text>
              </g>
            )}
          </motion.g>
        );
      })}
    </svg>
  );
};

/**
 * Get the center point of each territory polygon for label positioning.
 */
function getLabelPosition(territoryId: number): { x: number; y: number } {
  const centers: Record<number, { x: number; y: number }> = {
    1: { x: 205, y: 110 }, // ЦЕНТР — жёлтый квартал с небоскрёбами
    2: { x: 630, y: 170 }, // ИНДУСТРИАЛЬНАЯ ЗОНА — промышленная зона
    3: { x: 745, y: 380 }, // ЖИЛОЙ РАЙОН — жилой район с домами и деревьями
    4: { x: 290, y: 260 }, // ПРИГОРОДЬ — пригород с контейнерами
    5: { x: 290, y: 470 }, // ПОРТ — портовые доки с ящиками и грузами
    6: { x: 135, y: 220 }, // КИТАЙСКИЙ КВАРТАЛ — традиционные здания
  };
  return centers[territoryId] || { x: 400, y: 300 };
}
