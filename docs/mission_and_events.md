# Mission and Events Design

## Goals
- Provide clear mission lifecycle, event model, and data shape for implementation.
- Ensure transactional safety for mission start/complete and event processing.

## Mission (concept)
- id: PK
- name, description
- duration: seconds
- difficulty: enum (EASY, MEDIUM, HARD)
- slots: max characters allowed
- power_required / intellect_required / agility_required: thresholds
- reward_money, reward_influence: numeric rewards
- created_at

Notes: missions are templates. When a user starts a mission we create `UserMission` (instance).

## UserMission (instance)
- id: PK
- user_id -> users.id
- mission_id -> missions.id
- status: enum (PENDING, IN_PROGRESS, COMPLETED, FAILED)
- started_at, ends_at
- success_chance: numeric

Indexing: index on `user_id`, `ends_at` (for scheduled completion), `status`.

## MissionCharacter link
- id: PK
- user_mission_id -> user_missions.id
- character_id -> characters.id
- slot_number

## MissionEvent (attached to Mission template)
- id: PK
- mission_id -> missions.id
- event_type: enum (POLICE_RAID, COMPETITOR_ATTACK, RANDOM_LUCK, AMBUSH, EXTRA_REWARD)
- chance: integer 0..100 (percent chance to trigger when mission completes or at checkpoints)
- description: text
- parameters: JSON for event-specific payload (e.g., money_loss_pct, influence_penalty)

Behavior: when a mission completes (scheduled or forced), we process events in order; each event rolls (1..100) and if roll <= chance, apply effect.

## Event effects (examples)
- POLICE_RAID: subtract money up to parameter `max_loss` or percentage; can also increase wanted level.
- COMPETITOR_ATTACK: reduce influence by fixed or percent amount.
- RANDOM_LUCK: binary success/fail with extra reward or failure.
- AMBUSH: potentially injure character (future: durability/health) or remove character from roster.

## Balancing parameters
- Each mission has `reward_*` and `difficulty` which influence `success_chance` calculation.
- Characters provide stats (power/intellect/agility) plus weapons/tools bonuses.
- success_chance formula: base + f(total_power vs required) + f(total_intellect vs required) + modifiers from items and difficulty.

## Lifecycle & transactions
1. Start mission (atomic):
   - validate mission exists and characters meet constraints
   - create `UserMission` with status `IN_PROGRESS` and compute `ends_at`
   - lock/mark characters `is_busy=True`
   - create `MissionCharacter` links
   - All within a DB transaction (session.begin). Use commit=False in CRUD helpers when called inside transaction.

2. Complete mission (atomic):
   - only process when `ends_at` passed and status `IN_PROGRESS`
   - load UserMission, related characters and mission events (explicit queries, avoid lazy-loading)
   - evaluate events and determine success/failure
   - update UserMission.status, free characters (is_busy=False), award rewards or apply penalties
   - All updates inside a DB transaction

## Scheduling / background
- Use a background worker (Celery, RQ, or a lightweight scheduler) to poll `user_missions` where `ends_at <= now AND status = IN_PROGRESS` and call complete flow.
- Alternatively, process completion lazily when user interacts or via webhook from Telegram.

## API endpoints (initial)
- `GET /missions` — list mission templates
- `GET /missions/{id}` — mission details + events
- `POST /missions/{id}/start` — body: {character_ids: [..]}; returns `user_mission` id and `ends_at`
- `GET /user_missions` — list user's missions
- `POST /user_missions/{id}/complete` — admin/worker trigger to force-complete

Request/response shapes should use Pydantic schemas; validate ownership and character availability in router dependency.

## DB considerations
- Use explicit joins/SELECTs in service layer to avoid SQLAlchemy lazy-loading in async code.
- Use `expire_on_commit=False` for sessions used in tests/workers to make reading after commit simpler.
- Add FK cascade rules where appropriate (e.g., delete mission template -> keep or archive instances? prefer prevent-deletes).

## Next concrete steps
1. Define Pydantic schemas for `Mission`, `MissionEvent`, `UserMission`, `MissionCharacter` (for API).
2. Create ER diagram (simple) and add to `docs/`.
3. Implement or adjust migration(s) for any schema changes (enums/defaults).
4. Implement worker to process `ends_at` completions.

---
If хотите, начну с Pydantic схем и API spec (OpenAPI snippets). Или сразу нарисую ER (PlantUML/mermaid). Что предпочитаете? 
