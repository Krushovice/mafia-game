# Mafia Game — Telegram Mini App

## 🎮 Концепция игры

### Сеттинг
Игрок — **босс мафии**. Начинает с одного квартала, строит империю через миссии, захват территорий и управление бойцами.

### Стартовые условия
| Параметр | Значение |
|----------|----------|
| 💰 Mafia Coins | 1 000 |
| 🌐 Influence | 10 |
| ⚠️ Wanted Level | 0 |
| 👤 Бойцы | 1 Капо (универсальный) |
| 🏘️ Территории | 1 квартал |

### Механики

#### 🎯 Миссии
- **Обычные** — без таймера, игрок сам решает когда начать
- **Всплывающие (Flash)** — с таймером (как в Dispatch), больше награда, ограничены по времени доступности
- **Требования** — power / intellect / agility, проверка по сумме характеристик персонажей + экипировка
- **Слоты** — 1-3 персонажа на миссию

#### ⚡ Случайные события (10% шанс во время миссии)
| Событие | Варианты выбора |
|---------|----------------|
| **🚔 Облава копов** | 1. Откупиться (потеря денег) 2. Бездействие (провал миссии, -5 влияния) 3. Заговорить зубы (шанс зависит от влияния) |
| **⚔️ Атака конкурентов** | 1. Бой (зависит от влияния + оружия персонажей) 2. Откупиться (деньги) 3. Бездействие (провал) |
| **🍀 Случайная удача** | Бонус к награде (автоматический) |

> События требуют **выбора игрока** в реальном времени — не просто рандом, а интерактивное решение.

#### 🏘️ Захват территорий
- Специальные сложные миссии на **3 слота**
- Высокие требования к характеристикам
- Дают **пассивный доход** (coins/influence за тик)
- Увеличивают **максимальное влияние** (оттягивают победу)

#### ⚠️ Уровень розыска (Wanted Level)
- Растёт при выполнении миссий (+2-5 за миссию, зависит от типа)
- При **>80** — блокировка новых миссий
- Снижается со временем (реальное ожидание)
- **Донат**: небольшое ускорение снижения розыска (не P2W)

#### 🏪 Магазин бойцов
- Можно купить 1-2 дополнительных бойцов
- Разные типы: **Боевик** (power), **Хакер** (intellect), **Переговорщик** (agility)
- Цена зависит от характеристик

#### 🏆 Условие победы
- **100 влияния** — базовая победа
- Захват территорий **расширяет лимит** (100 + 10 за каждую территорию)
- Игра **бесконечная** — всегда есть чем заняться

---

## 📊 Анализ текущего состояния

### Архитектура
- **Backend**: FastAPI + SQLAlchemy (async) + PostgreSQL
- **Bot**: aiogram 3.x (только `/start` с WebApp кнопкой)
- **Аутентификация TMA**: `X-Telegram-InitData` header + HMAC-SHA256 валидация
- **CORS**: настроен для Telegram доменов

### Что уже работает
| Функция | Статус |
|---------|--------|
| Регистрация пользователя | ✅ |
| Ресурсы (money, influence, wanted_level) | ✅ |
| Персонажи (CRUD + экипировка) | ✅ |
| Миссии (создание, список, старт) | ✅ |
| UserMissions (старт, завершение) | ✅ |
| Оружие/Инструменты (CRUD) | ✅ |
| События миссий (CRUD) | ✅ |
| TMA Auth (initData валидация) | ✅ |
| CORS middleware | ✅ |
| Bot `/start` с WebApp кнопкой | ✅ |

### Что нужно доработать / добавить

#### Критичные баги
- [x] Fixed: indentation в handlers.py
- [ ] `complete_mission` **не начисляет награды** (TODO в коде)
- [ ] `complete_mission` **не обрабатывает события с выбором** — сейчас рандом без интерактива
- [ ] Нет валидации ownership для экипировки

#### Новые модели (БД)
- [ ] **Territory** — территории для захвата
- [ ] **UserTerritory** — связь пользователь ↔ территория
- [ ] **ShopItem** — товары магазина (бойцы, экипировка)
- [ ] **MissionEventChoice** — варианты выбора для событий
- [ ] **MissionEventType** — расширить enum (police_raid, competitor_attack, random_luck)
- [ ] **UserMissionEventLog** — лог событий в активной миссии (для интерактивных выборов)

#### Новые enum
- [ ] `EventChoiceType` — payoff, fight, talk, do_nothing
- [ ] `MissionType` — regular, flash, territory
- [ ] `TerritoryType` — district, neighborhood, borough

#### Новые сервисы
- [ ] **TerritoryService** — захват, пассивный доход
- [ ] **ShopService** — покупка бойцов/экипировки
- [ ] **WantedLevelService** — рост/снижение розыска
- [ ] **MissionEventService** — обработка событий с выбором игрока

#### Новые эндпоинты
- [ ] `POST /missions/{id}/respond_event` — ответ на событие
- [ ] `GET /territories` — список территорий
- [ ] `POST /territories/{id}/capture` — начать захват
- [ ] `GET /shop` — магазин
- [ ] `POST /shop/buy/{item_id}` — покупка
- [ ] `GET /tma/dashboard` — агрегированные данные для TMA
- [ ] `POST /wanted/cooldown` — снизить розыск (время/донат)

#### Геймплейные доработки
- [ ] Стартовый пакет: 1000 coins, 10 influence, 0 wanted, 1 capo
- [ ] Wanted level растёт от миссий
- [ ] Блокировка миссий при wanted > 80
- [ ] Flash миссии с таймером доступности
- [ ] Territory capture missions (3 слота)
- [ ] Пассивный доход от территорий
- [ ] Интерактивные события (выбор игрока, не рандом)

---

## 🗂️ План реализации (Backend)

### Шаг 1: Расширение моделей и enum
**Файлы**: `src/core/database/models/enums.py`, новые модели

#### 1.1. Новые enum
```python
class MissionType(str, enum.Enum):
    REGULAR = "regular"       # обычная, без таймера
    FLASH = "flash"           # всплывающая, с таймером доступности
    TERRITORY = "territory"   # захват территории

class EventChoiceType(str, enum.Enum):
    PAYOFF = "payoff"         # откупиться
    FIGHT = "fight"           # бой
    TALK = "talk"             # заговорить зубы
    DO_NOTHING = "do_nothing" # бездействие

class TerritoryType(str, enum.Enum):
    DISTRICT = "district"
    NEIGHBORHOOD = "neighborhood"
    BOROUGH = "borough"
```

#### 1.2. Модель Territory
```python
class Territory(Base):
    id: int
    name: str
    description: str
    territory_type: TerritoryType
    power_required: int
    intellect_required: int
    agility_required: int
    passive_income_money: int      # за тик
    passive_income_influence: int  # за тик
    influence_cap_bonus: int       # +к макс. влиянию
    is_captured: bool              # захвачена кем-то
    captured_by_user_id: int | None  # FK -> users
```

#### 1.3. Модель ShopItem
```python
class ShopItem(Base):
    id: int
    name: str
    description: str
    item_type: str  # "character", "weapon", "tool"
    cost_money: int
    cost_influence: int
    character_role: CharacterRole | None  # если тип character
    character_trait: CharacterTrait | None
    base_power: int
    base_intellect: int
    base_agility: int
    bonus_power: int  # для оружия
    bonus_intellect: int  # для инструментов
    bonus_agility: int
    is_available: bool
```

#### 1.4. Модель MissionEventChoice
```python
class MissionEventChoice(Base):
    id: int
    event_id: int  # FK -> mission_events
    choice_type: EventChoiceType
    label: str  # "Откупиться", "Бой", "Заговорить зубы"
    description: str
    # Параметры успеха
    influence_required: int
    power_required: int
    money_cost: int
    success_chance_base: int  # базовый шанс
```

#### 1.5. Модель UserMissionEventLog
```python
class UserMissionEventLog(Base):
    id: int
    user_mission_id: int  # FK -> user_missions
    event_id: int  # FK -> mission_events
    choice_type: EventChoiceType | None  # null если ещё не выбран
    result: str | None  # "success", "fail", "partial"
    resolved: bool  # выбран ли ответ
```

#### 1.6. Обновление Mission
```python
# Добавить в Mission:
mission_type: Mapped[MissionType]  # regular / flash / territory
flash_available_until: datetime | None  # для flash миссий
flash_reward_multiplier: float  # множитель награды для flash
```

#### 1.7. Обновление UserMission
```python
# Добавить в UserMission:
mission_type: Mapped[MissionType]
current_event_log_id: int | None  # текущее активное событие (требует выбора)
```

---

### Шаг 2: CRUD для новых моделей
**Файл**: `src/crud/other_crud.py`

- `CRUDTerritory` — list, get, capture
- `CRUDShopItem` — list, get, buy
- `CRUDMissionEventChoice` — list_by_event
- `CRUDUserMissionEventLog` — create, update, get_active

---

### Шаг 3: Сервисы

#### 3.1. MissionService — переработка
**Файл**: `src/services/mission_service.py`

- `start_mission()` — добавить проверку wanted < 80
- `complete_mission()` — **начисление наград** + wanted level рост
- `trigger_random_event()` — 10% шанс, создаёт UserMissionEventLog
- `respond_to_event()` — **новый метод**: обработка выбора игрока
- `_resolve_police_raid()` — логика облавы
- `_resolve_competitor_attack()` — логика атаки
- `_resolve_random_luck()` — логика удачи

#### 3.2. TerritoryService (новый)
**Файл**: `src/services/territory_service.py`

- `list_available()` — территории для захвата
- `capture_start()` — начать захват (создаёт UserMission типа TERRITORY)
- `capture_complete()` — при успехе: привязать к пользователю, включить пассивный доход
- `process_passive_income()` — тик дохода

#### 3.3. ShopService (новый)
**Файл**: `src/services/shop_service.py`

- `list_items()` — доступные товары
- `buy_character()` — покупка бойца (создаёт Character)
- `buy_equipment()` — покупка оружия/инструментов

#### 3.4. WantedLevelService (новый)
**Файл**: `src/services/wanted_service.py`

- `increase()` — рост после миссии
- `decrease_over_time()` — снижение со временем
- `is_blocked()` — проверка wanted > 80
- `apply_cooldown()` — ускоренное снижение (донат)

#### 3.5. UserService — доработка
**Файл**: `src/services/user_service.py`

- `get_or_create_by_telegram()` — **стартовый пакет**: 1000 coins, 10 influence, 0 wanted, 1 capo

---

### Шаг 4: API роутеры

#### 4.1. `src/api/routers/tma.py` (новый)
```
GET  /tma/dashboard          — все данные для главной (ресурсы, персонажи, миссии, территории)
GET  /tma/mission/{id}       — детали миссии с событиями
POST /tma/mission/{id}/respond_event — ответ на событие
```

#### 4.2. `src/api/routers/territory.py` (новый)
```
GET    /territories           — список территорий
POST   /territories/{id}/capture — начать захват
```

#### 4.3. `src/api/routers/shop.py` (новый)
```
GET    /shop                  — магазин
POST   /shop/buy/{item_id}    — покупка
```

#### 4.4. `src/api/routers/wanted.py` (новый)
```
GET    /wanted/status         — статус розыска + cooldown timer
POST   /wanted/cooldown       — снизить розыск
```

#### 4.5. Обновить существующие
- `mission.py` — добавить `mission_type`, flash миссии
- `user_missions.py` — добавить event log в ответ
- `equipment.py` — добавить ownership валидацию

---

### Шаг 5: Миграции
**Файлы**: `alembic/versions/`

- Добавить новые таблицы: territories, shop_items, mission_event_choices, user_mission_event_logs
- Добавить колонки в missions: mission_type, flash_available_until, flash_reward_multiplier
- Добавить колонки в user_missions: mission_type, current_event_log_id

---

### Шаг 6: Фоновые задачи
**Файл**: `src/services/mission_auto_complete.py`

- Авто-завершение миссий по таймеру
- Пассивный доход от территорий (каждые N минут)
- Снижение wanted level со временем

---

## 🗂️ План реализации (Frontend — TMA)

### Стек
- **React + Vite + TypeScript**
- **TailwindCSS** (адаптация под Telegram тему)
- **Zustand** (state management)
- **Telegram WebApp SDK**

### Экраны
1. **Dashboard** — ресурсы, карта территорий, активные миссии
2. **Characters** — список бойцов, экипировка, создание
3. **Missions** — доступные миссии (regular + flash), запуск
4. **Mission Active** — прогресс, события (выбор!), результат
5. **Territories** — карта, захват
6. **Shop** — покупка бойцов и экипировки
7. **Wanted** — статус розыска, cooldown

---

## 📋 Чеклист (Backend)

### Модели и миграции
- [ ] Расширить enums (MissionType, EventChoiceType, TerritoryType)
- [ ] Создать модель Territory
- [ ] Создать модель ShopItem
- [ ] Создать модель MissionEventChoice
- [ ] Создать модель UserMissionEventLog
- [ ] Обновить Mission (mission_type, flash поля)
- [ ] Обновить UserMission (mission_type, current_event_log_id)
- [ ] Написать Alembic миграции

### CRUD
- [ ] CRUDTerritory
- [ ] CRUDShopItem
- [ ] CRUDMissionEventChoice
- [ ] CRUDUserMissionEventLog

### Сервисы
- [ ] MissionService: начисление наград
- [ ] MissionService: wanted level рост
- [ ] MissionService: trigger_random_event
- [ ] MissionService: respond_to_event (интерактивные события)
- [ ] TerritoryService
- [ ] ShopService
- [ ] WantedLevelService
- [ ] UserService: стартовый пакет (capo + ресурсы)
- [ ] Auto-complete фоновая задача

### API
- [ ] TMA роутер (dashboard, mission detail, respond_event)
- [ ] Territory роутер
- [ ] Shop роутер
- [ ] Wanted роутер
- [ ] Ownership валидация для equipment
- [ ] Проверка wanted < 80 при старте миссии

---

## 🔒 Безопасность

1. **InitData валидация** — каждый TMA запрос
2. **Ownership checks** — только свои персонажи/экипировка
3. **Server-side event resolution** — клиент не решает исход событий
4. **Rate limiting** — защита от спама
5. **HTTPS only**

---

## 🚀 Порядок реализации

```
Приоритет 1 (критично для геймплея):
  1. Начисление наград в complete_mission
  2. Стартовый пакет (capo + ресурсы)
  3. Wanted level механика (рост, блокировка >80)
  4. Интерактивные события (выбор игрока)

Приоритет 2 (основной геймплей):
  5. Territory модель + захват
  6. Shop модель + покупка бойцов
  7. Flash миссии
  8. Пассивный доход от территорий

Приоритет 3 (полировка):
  9. Фоновые задачи (авто-завершение, cooldown)
  10. TMA dashboard endpoint
  11. Ownership валидация
  12. Миграции
```
