# Project Rules

## Architecture
- Service layer handles all business logic
- Repositories handle DB only
- Routers are thin

## aiogram
- Use routers, not Dispatcher directly
- Handlers must be minimal

## Database
- Always use async session
- Use select() instead of raw SQL

## Style
- No global state
- No blocking code
- Use dependency injection
