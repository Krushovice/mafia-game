# Production Frontend Structure (Telegram Mini App Game)

## Architecture: Feature-Sliced Design (FSD)

    src/
      app/
        providers/
          query-provider.tsx
          router-provider.tsx
        styles/
        index.tsx

      pages/
        dashboard/
          ui/
            dashboard-page.tsx
          index.ts

        missions/
          ui/
            missions-page.tsx
          index.ts

        mission-active/
          ui/
            mission-active-page.tsx
          index.ts

        characters/
          ui/
            characters-page.tsx
          index.ts

        shop/
          ui/
            shop-page.tsx
          index.ts

        territories/
          ui/
            territories-page.tsx
          index.ts

        wanted/
          ui/
            wanted-page.tsx
          index.ts

      widgets/
        header/
          ui/
            header.tsx

        sidebar/
          ui/
            sidebar.tsx

        resource-bar/
          ui/
            resource-bar.tsx

        mission-card/
          ui/
            mission-card.tsx

      features/
        auth/
          model/
            use-auth.ts
          api/
            auth-api.ts

        start-mission/
          model/
            use-start-mission.ts

        mission-choice/
          model/
            use-mission-choice.ts

        buy-item/
          model/
            use-buy-item.ts

      entities/
        user/
          model/
            types.ts
            store.ts

        mission/
          model/
            types.ts
            store.ts
          api/
            mission-api.ts

        character/
          model/
            types.ts
          api/
            character-api.ts

        territory/
          model/
            types.ts

        resource/
          model/
            types.ts

      shared/
        api/
          base-api.ts

        lib/
          telegram/
            telegram.ts

        config/
          routes.ts

        ui/
          button/
          card/
          modal/

        hooks/
          use-init.ts

        types/
          global.d.ts

------------------------------------------------------------------------

## Layer Responsibilities

### app/

-   Providers (React Query, Router)
-   Global styles
-   App initialization

------------------------------------------------------------------------

### pages/

-   Route-level components
-   Compose widgets & features
-   No business logic

------------------------------------------------------------------------

### widgets/

-   Large UI blocks
-   Combine entities + features
-   Example: header, mission list

------------------------------------------------------------------------

### features/

-   User actions (business logic)
-   API calls + state
-   Example: start mission, choose action

------------------------------------------------------------------------

### entities/

-   Core game models
-   Types + API + state
-   Example: mission, character, user

------------------------------------------------------------------------

### shared/

-   Reusable infrastructure
-   UI kit
-   API base client
-   Telegram SDK wrapper

------------------------------------------------------------------------

## Data Flow

    Page → Widget → Feature → Entity → API → Backend

------------------------------------------------------------------------

## Example Flow: Start Mission

1.  User clicks button (widget)
2.  Feature handles action (use-start-mission)
3.  Calls entity API (mission-api)
4.  Backend responds
5.  React Query updates cache
6.  UI re-renders

------------------------------------------------------------------------

## API Base Setup

    shared/api/base-api.ts

Responsibilities: - base URL - auth headers - error handling

------------------------------------------------------------------------

## Telegram Integration

    shared/lib/telegram/telegram.ts

Responsibilities: - init WebApp - get user - send initData to backend

------------------------------------------------------------------------

## State Strategy

-   Server state → React Query
-   Client/global state → Zustand (optional)

------------------------------------------------------------------------

## Naming Conventions

-   kebab-case folders
-   camelCase variables
-   feature-based naming

------------------------------------------------------------------------

## Scaling Rules

-   No direct API calls from pages
-   No business logic in UI
-   Features are isolated
-   Entities are reusable

------------------------------------------------------------------------

## MVP Priority

1.  missions
2.  mission-active
3.  dashboard

Then: - characters - shop - territories

------------------------------------------------------------------------

## Key Principle

Game logic lives in backend. Frontend = renderer + user input.
