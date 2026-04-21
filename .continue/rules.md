# Development Rules for Mafia TMA Project

## Code Style

### Python Backend
- Use 80 character line length limit
- Follow PEP 8 style guide
- Use `black`, `isort`, and `ruff` for formatting
- Type hints required in all functions
- Use async/await for I/O operations

### TypeScript Frontend  
- Use 80 character line length limit
- Enable strict mode in tsconfig
- Use ESLint with recommended rules
- Types must be defined for all props and state
- Use React hooks consistently (useState, useEffect, etc.)

## Project Structure

### Backend (`src/`)
```
src/
├── api/          # FastAPI routers and endpoints
├── bot/          # Telegram Bot handlers
├── core/         # Core configuration and utilities
├── crud/         # Base CRUD operations
├── schemas/      # Pydantic schemas for validation
├── services/     # Business logic services
└── scripts/      # Data seeding and maintenance scripts
```

### Frontend (`frontend/src/`)
```
frontend/src/
├── api/          # API client functions
├── entities/     # Domain entities (character, mission, etc.)
├── features/     # Feature-based components
├── pages/        # Page-level components
├── shared/       # Shared UI components and utilities
└── widgets/      # Reusable widget components
```

## API Conventions

### Request Format
- Use JSON with proper content-type headers
- Authentication via Telegram WebApp or JWT tokens
- Error responses include status code and message

### Response Format
```json
{
  "success": true,
  "data": { ... },
  "message": null
}
```

## Database Conventions

### Models
- Use SQLAlchemy with async support
- All models must have `id`, `created_at`, `updated_at` fields
- Foreign keys should use proper cascade rules where appropriate

### Migrations
- Use Alembic for database migrations
- Migration files named: `YYYY_MM_DD_HHMMSS_description.py`
- Always test migrations in development before production

## Testing

### Backend Tests
- Use pytest with async support
- Test coverage target: 80%+
- Include integration tests for critical endpoints

### Frontend Tests  
- Use Vitest for unit tests
- Use React Testing Library for component tests
- E2E tests with Playwright or similar

## Deployment

### Environment Variables
```env
# Backend
DATABASE_URL=postgresql://...
BOT_TELEGRAM_TOKEN=...
BOT_WEBHOOK_URL=...
API_SECRET_KEY=...

# Frontend (embedded in build)
VITE_API_BASE_URL=https://api.example.com
```

### Docker
- Use multi-stage builds for production images
- Separate containers: api, bot, postgres, redis
- Health checks required for all services

## Security

- Never commit secrets or tokens to git
- Use environment variables for sensitive data
- Implement rate limiting on API endpoints
- Validate and sanitize all user inputs
- Use HTTPS in production

## Git Workflow

### Branching
- `main` - Production-ready code
- `develop` - Integration branch
- Feature branches: `feature/xxx`, `fix/xxx`

### Commit Messages
- Use conventional commits format
- Examples:
  ```
  feat: add new mission template system
  fix: resolve territory capture calculation bug
  docs: update API documentation
  style: reformat code with black
  refactor: improve error handling in user service
  ```

## Communication

### Pull Requests
- Include description of changes
- Link to related issues
- Add tests for new features
- Update documentation as needed

### Code Reviews
- Check for bugs and security issues
- Verify test coverage
- Ensure code follows project conventions
- Review performance implications
