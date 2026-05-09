---
name: ship-changes
description: Используй этот скилл когда пользователь хочет автоматически прогнать полный pipeline по новым изменениям в проекте — сгенерировать тесты на изменённый код, запустить все проверки (ruff/isort/black/pytest/eslint/tsc), при успехе закоммитить и запушить в git, затем проверить статус GitHub Actions workflow и выдать итоговый отчёт. Активируется на фразы "ship", "запусти pipeline", "прогони изменения", "auto-commit", "отправь изменения с тестами", "/ship-changes".
argument-hint: [--no-tests] [--no-push] [--message "commit msg"]
allowed-tools: [Read, Write, Edit, Bash, Glob, Grep]
---

# ship-changes — Авто-pipeline для изменений

Полный конвейер: новые изменения → тесты → проверки → commit → push → статус workflow → отчёт.

## Когда вызывать

- Юзер сказал "ship", "/ship-changes", "запусти pipeline", "прогони изменения с тестами"
- Юзер хочет одной командой довести diff до зелёного CI

## Когда НЕ вызывать

- Diff пустой (нет изменений) — сообщи и выйди
- Юзер явно сказал "не коммить" / "только посмотри" — этот скилл всегда нацелен на push

## Аргументы

Парсятся из `$ARGUMENTS`:
- `--no-tests` — пропустить генерацию тестов, только прогнать существующие
- `--no-push` — закоммитить, но не пушить
- `--message "..."` — кастомное сообщение коммита (иначе сгенерируется автоматически)

---

## Pipeline (строго по шагам)

### Шаг 1. Снимок изменений

```bash
git status --porcelain
git diff --stat
git diff --name-only
git diff --cached --name-only
```

Классифицируй файлы:
- **backend**: `*.py` в `src/`
- **frontend**: `*.ts`, `*.tsx` в `frontend/src/`
- **migrations**: `alembic/versions/*.py`
- **infra**: `docker-compose.yaml`, `*.yml`, `pyproject.toml`, `package.json`
- **docs**: `*.md`, `docs/*`
- **tests**: `tests/*.py`

Если все файлы — только docs/infra без кода → пропусти шаг 2 (генерацию тестов).

Если diff пустой → выйди с сообщением "Нет изменений для отправки".

### Шаг 2. Генерация тестов (если `--no-tests` не задан)

Для **backend** изменений:
- Прочитай каждый изменённый `.py` файл целиком
- Найди новые/изменённые публичные функции, классы, эндпоинты, сервисы
- Для каждого изменённого модуля проверь, есть ли соответствующий тест в `tests/`:
  - `src/services/foo.py` → `tests/test_foo.py`
  - `src/api/routers/bar.py` → `tests/test_bar.py`
- Если теста нет — создай файл по образцу существующих (см. `tests/test_mission.py`, `tests/test_territory.py`)
- Если тест есть, но новая функция не покрыта — добавь test-функцию
- Используй `pytest-asyncio` (`asyncio_mode = auto` уже включён в pytest.ini)
- Для роутеров — fixture `client` из `tests/conftest.py`
- Тесты на русском в docstring, имена функций английские

Для **frontend** изменений:
- В проекте НЕТ vitest/jest
- НЕ создавай test-файлы для фронта — только прогон tsc + eslint в шаге 3
- Если хочется типобезопасности — проверь, что новые типы экспортируются из `src/types.ts`

Для **migrations**:
- Не генерируй тесты для самих миграций
- Но если миграция добавляет колонку, на которую смотрит сервис — тест на сервис обязателен

Покажи юзеру список созданных/обновлённых тестов перед запуском.

### Шаг 3. Прогон проверок

**Pre-flight: CI parity check** — локальный pytest может проходить из-за editable install (`.pth` в `.venv`), а CI ставит только `requirements.txt`. Перед коммитом убедись что:
- `pytest.ini` содержит `pythonpath = src` (или эквивалентный механизм), ИЛИ CI делает `pip install -e .`
- Все импорты из тестов покрыты через `requirements.txt` (не optional `[bot]`/`[dev]` extras, если CI их не ставит)
- `requires-python` в `pyproject.toml` совместим с матрицей Python в `.github/workflows/*.yml`

Быстрая симуляция CI:
```bash
python3 -m venv /tmp/ci-sim && /tmp/ci-sim/bin/pip install -q -r requirements.txt pytest pytest-asyncio aiosqlite
/tmp/ci-sim/bin/pytest -q
```

Если падает — фикс в первую очередь, до запуска основных проверок.

Backend (если есть `*.py` изменения):
```bash
ruff check .
isort --check-only .
black --check .
pytest -q
```

Frontend (если есть изменения в `frontend/src/`):
```bash
cd frontend && npm run lint
cd frontend && npx tsc -b --noEmit
```

**Стратегия при ошибках:**
- Lint ошибки (ruff/isort/black/eslint) — запусти автофикс: `ruff check --fix .`, `isort .`, `black .`. Re-run проверку.
- Test failures — НЕ автофикси. Покажи юзеру вывод и спроси: чинить код, чинить тест, или прервать?
- tsc ошибки — НЕ автофикси, покажи и спроси.

Если что-то упало и не чинится автоматом — стоп. Не коммить.

### Шаг 4. Коммиты (granular!)

**ЖЁСТКОЕ ПРАВИЛО: один логический change → один коммит.** НЕ один мегакоммит на всё.

Группируй staged-файлы по логическим единицам:

| Тип изменения | Что входит в один коммит |
|---|---|
| Новая фича | Все файлы фичи (модель + миграция + сервис + роутер + тесты на эту фичу) |
| Bugfix | Только файлы с фиксом + тест на регрессию |
| Новая зависимость | `pyproject.toml`/`requirements.txt`/`uv.lock`/`package.json`/`package-lock.json` — отдельный коммит `chore: add <lib>` |
| Удаление зависимости | Аналогично — отдельный `chore: drop <lib>` |
| Миграция Alembic | Отдельный коммит `feat(db):` или `chore(db):` если структурное изменение независимо от кода |
| Конфиг линтеров/CI | `pyproject.toml [tool.*]`, `.github/workflows/*` — отдельно `chore: configure <tool>` |
| Авто-форматирование | Отдельный коммит `style: ruff/isort/black autofix` (не смешивать с фичей) |
| Docs | `*.md`, картинки — отдельный `docs:` |
| Удалённые файлы | Если осмысленные (старые правила, мёртвый код) — `chore: remove obsolete <name>` |
| Скиллы Claude | `.claude/skills/*` — отдельный `chore(claude): add/update skill` |
| Frontend types | `frontend/src/types.ts` обновления типов — отдельно от UI-кода если меняют контракт |
| Восстановление файла | Отдельно `fix: restore <file>` если файл был удалён зря |

**Алгоритм:**
1. Из снапшота `git diff --name-only` сгруппируй файлы по таблице выше
2. Для каждой группы: `git add <файлы группы>` → отдельный `git commit`
3. Если файл попадает в две группы — он принадлежит наиболее семантически важной (фича > форматирование)
4. Чисто-форматные правки одного файла НЕ смешивать с логическими — выноси в `style:` коммит

Сгенерируй commit message в стиле проекта (см. `git log --oneline -10`):
- Conventional Commits: `feat:`, `fix:`, `refactor:`, `docs:`, `test:`, `chore:`, `style:`, `build:`, `ci:`
- Subject ≤ 72 chars, на русском (если в недавних коммитах русский) или английском
- Body — только если "почему" неочевидно

Если задан `--message` — используй его дословно для **первого** коммита; остальные коммиты-сателлиты сгенерируй автоматически.

Коммит с co-author (для каждого):
```bash
git commit -m "$(cat <<'EOF'
<subject>

<body if needed>

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
EOF
)"
```

**Перед каждым коммитом** в multi-commit пайплайне проверяй `git status --porcelain` чтобы убедиться что застейжены только нужные файлы.

### Шаг 5. Push (если `--no-push` не задан)

```bash
git rev-parse --abbrev-ref HEAD  # текущая ветка
git push origin <branch>
```

Если ветка не tracked:
```bash
git push -u origin <branch>
```

**НЕ** force push. Если push отклонён — стоп, покажи ошибку юзеру.

### Шаг 6. Проверка GitHub Actions workflow

Проверь наличие `gh`:
```bash
command -v gh
```

**Если `gh` есть:**
```bash
gh run list --branch $(git rev-parse --abbrev-ref HEAD) --limit 1 --json databaseId,status,conclusion,workflowName,url
gh run watch <run-id> --exit-status  # ждёт завершения, exit code = успех
```

**Если `gh` нет:**
- Получи remote URL: `git remote get-url origin`
- Извлеки `owner/repo` из URL
- Сформируй ссылку: `https://github.com/<owner>/<repo>/actions`
- Сообщи юзеру: "gh CLI не установлен — workflow статус проверь вручную: <url>"
- Не делай curl с токеном без явного разрешения юзера

Таймаут ожидания workflow: **15 минут**. Если дольше — выйди с пометкой "workflow ещё идёт".

### Шаг 7. Итоговый отчёт

Формат отчёта (всегда в конце, даже при ошибках):

```
## Ship Report

**Branch:** <branch>
**Commit:** <sha> — <subject>

### Изменения
- <file1> (<+lines>/<-lines>)
- <file2> (<+lines>/<-lines>)

### Тесты
- Создано: <N> файлов / <M> функций
- Обновлено: <K> файлов
- Пропущено: <причина>

### Проверки
- ruff: ✅ / ❌
- isort: ✅
- black: ✅
- pytest: ✅ <N passed>
- eslint: ✅
- tsc: ✅

### Git
- Commit: ✅ <sha>
- Push: ✅ origin/<branch>

### CI Workflow
- Status: ✅ success / ❌ failure / ⏳ in_progress / ⚠️ gh_not_installed
- URL: <workflow run url>
- Длительность: <Ns>

### Следующие шаги
- <если CI красный — что чинить>
- <если CI зелёный — "готово к merge">
```

---

## Жёсткие правила

1. **НЕ** запускай `git push --force` ни при каких условиях
2. **НЕ** коммить, если хоть одна проверка красная
3. **НЕ** генерируй тесты для тривиальных изменений (опечатки, форматирование, чистый рефакторинг переименования)
4. **НЕ** трогай `.env`, секреты, ключи — если такие файлы в diff, останови pipeline и предупреди
5. **НЕ** делай `git add -A` — добавляй только конкретные файлы из diff
6. **НЕ** обходи hooks (`--no-verify`) и подпись (`--no-gpg-sign`)
7. Если диалог нужен (тесты упали, мердж-конфликт, неясный intent) — спроси юзера, не угадывай
8. **НЕ** один мегакоммит на всё — разбивай по логике (см. Шаг 4: фича / зависимость / миграция / docs / linter-config / autoformat — каждое отдельным коммитом)
9. **НЕ** пропускай CI-parity check — локальная зелень не равна CI-зелень. Симулируй чистый venv (Шаг 3 pre-flight) если вносил изменения в импорты/зависимости/`pytest.ini`

---

## Пример прогона

Юзер: `/ship-changes`

```
Шаг 1: Diff содержит:
  - src/services/wanted_service.py (+45/-12)
  - frontend/src/pages/wanted/Wanted.tsx (+30/-0)

Шаг 2: Генерирую tests/test_wanted_service.py — 3 теста на новые функции
        Frontend без unit-тестов (нет vitest), только tsc+eslint

Шаг 3: ruff ✅ | isort ✅ | black ✅ | pytest 24 passed ✅
       eslint ✅ | tsc ✅

Шаг 4: Commit "feat: add wanted_service auto-decay logic"

Шаг 5: Push origin/main ✅

Шаг 6: gh run watch — workflow #142 success в 2m 14s ✅

Шаг 7: [отчёт]
```
