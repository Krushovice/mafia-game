# 🏗️ Progress Log — Mafia TMA

> Обновлён: 14 апреля 2026

---

## ✅ Выполнено (список всех изменений)

### Бэкенд (уже было до начала работ)
- [x] Модели: Territory, UserTerritory, NPCBoss, TerritoryType enum
- [x] CRUD: CRUDTerritory, CRUDUserTerritory
- [x] TerritoryService: list_for_user, start_capture, collect_passive_income
- [x] API: GET /territories/, GET /territories/income, POST /territories/{id}/capture, GET /map/
- [x] Миграции: territory system + npc_bosses + territory grid
- [x] Seed: 8 территорий, 8 NPC-боссов
- [x] Миссии: POST /missions/{id}/start, POST /user_missions/{id}/complete, GET /user_missions/{id}/active_event
- [x] События: POST /user_missions/{id}/respond_event

### Фронтенд — выполнено в этой сессии
- [x] **MissionCard onStart** — миссии можно запускать с выбором бойца (MissionsPage)
- [x] **useStartMission hook** — интегрирован в UI
- [x] **MissionActivePage** — события теперь poll-ятся с бэкенда (GET /user_missions/{id}/active_event), убран хардкод
- [x] **BottomNav** — 4 таба: 🗺️ Карта, 🏪 Магазин, 👤 Бойцы, ❓ Помощь
- [x] **Help-экран** (`/help`) — FAQ по геймплею
- [x] **Формулы влияния** (`shared/lib/territory.ts`) — influenceThreshold, passiveIncomeCoins, influenceCapBonus
- [x] **Типизация** — добавлены `reward_influence`, `mission_type`, `is_busy`, `ActiveEvent`
- [x] **Удалён dead code** — TerritoryGrid widget (был с @ts-nocheck)
- [x] **SVG-карта города** — 8 цветных полигонов, hover, glow, береговая линия острова, подписи
- [x] **Экран района** (`/territories/:id`) — мини-карта с кружками миссий, запуск миссий, кнопка захвата

### Новые файлы
```
frontend/src/entities/map/
  ├── model/types.ts         # MapTerritory, NPCBoss, MapResponse
  ├── api/map-api.ts         # mapApi.getMap()
  └── index.ts

frontend/src/widgets/city-map/
  ├── ui/CityMap.tsx         # SVG-карта с полигонами
  └── index.ts

frontend/src/pages/district/
  ├── ui/DistrictPage.tsx    # Экран района с кружками миссий
  └── index.ts

frontend/src/pages/help/
  ├── ui/HelpPage.tsx        # FAQ-страница
  └── index.ts

frontend/src/shared/lib/
  └── territory.ts           # influenceThreshold, passiveIncomeCoins, influenceCapBonus

frontend/src/shared/hooks/
  ├── use-telegram-native.ts # Telegram Native features hook
  └── index.ts               # Hook exports

frontend/src/shared/ui/toast/
  ├── toast-store.ts         # Zustand toast store
  ├── ToastContainer.tsx     # Toast UI component with Framer Motion
  └── index.ts               # Toast exports

frontend/src/shared/error-boundary/
  ├── ErrorBoundary.tsx      # React Error Boundary component
  └── index.ts               # Error boundary exports

frontend/src/lib/telegram/
  └── telegram.ts            # Telegram WebApp init and theme helpers
```

### Изменённые файлы
```
frontend/src/pages/map/ui/MapPage.tsx        # Добавлен ToastContainer
frontend/src/pages/district/ui/DistrictPage.tsx  # Framer Motion анимации, фильтрация по territory_id, ToastContainer
frontend/src/widgets/city-map/ui/CityMap.tsx  # Framer Motion entrance/hover animations, haptic feedback
frontend/src/widgets/bottom-nav/ui/BottomNav.tsx  # Haptic feedback on nav, safe-area-inset-bottom
frontend/src/app/providers/router-provider.tsx     # Добавлен ToastContainer в Layout
frontend/src/app/index.tsx                     # Обёрнуто в ErrorBoundary
frontend/src/entities/mission/model/types.ts   # Добавлен territory_id
frontend/src/types.ts                          # Добавлен territory_id в Mission
frontend/src/shared/types/global.d.ts          # Расширены типы Telegram WebApp (MainButton, HapticFeedback)
frontend/src/index.css                         # Safe area CSS variables, expanded theme variables
```

---

## ⏳ Что осталось доделать

### 🔴 Критично
| # | Задача | Где | Оценка |
|---|--------|-----|--------|
| 1 | Пассивный доход — background task каждые 10 мин | Бэкенд | 2-3ч |
| 2 | Фильтрация миссий по `territory_id` в DistrictPage | Бэкенд + фронтенд | 1ч |
| 3 | Позиции кружков миссий привязать к `position_x`/`position_y` | Фронтенд | 0.5ч |

### 🟡 Важно
| # | Задача | Где | Оценка |
|---|--------|-----|--------|
| 4 | Telegram Native: themeParams, MainButton, Haptic | ✅ Фронтенд | ГОТОВО |
| 5 | Framer Motion анимации (переходы, пульсация) | ✅ Фронтенд | ГОТОВО |
| 6 | Safe areas (iPhone notch) | ✅ Фронтенд | ГОТОВО |
| 7 | Toast-уведомления | ✅ Фронтенд | ГОТОВО |

### 🔵 Желательно
| # | Задача | Где | Оценка |
|---|--------|-----|--------|
| 8 | React Query prefetch | Фронтенд | 0.5ч |
| 9 | Error boundaries | ✅ Фронтенд | ГОТОВО |
| 10 | Offline режим (кэш) | Фронтенд | 1ч |
| 11 | Wanted cooldown | Бэкенд | 0.5ч |

---

## 🎮 Как протестировать через бота

1. Открыть бота в Telegram
2. Нажать кнопку «Играть» / `MenuButton` → откроется TMA
3. **Главный экран** — SVG-карта города с 8 кварталами
   - Клик по любому кварталу → панель с деталями
   - Свой квартал → кнопка «Открыть район»
   - Чужой → кнопка «Захватить район»
4. **Экран района** — мини-карта с кружками миссий
   - Клик на кружок → выбор бойца → запуск миссии
5. **BottomNav**:
   - 🗺️ Карта → MapPage
   - 🏪 Магазин → ShopPage
   - 👤 Бойцы → CharactersPage
   - ❓ Помощь → HelpPage (FAQ)
6. **/missions** — список доступных миссий (tabs: Обычные / Flash)
   - Клик «Начать миссию» → character select → запуск

---

## 📦 Запуск

```bash
docker compose up -d --build
```

Фронтенд: `http://localhost:3000`
Бэкенд: `http://localhost:8000`
