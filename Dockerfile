FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV POETRY_VIRTUALENVS_CREATE=false

COPY pyproject.toml pyproject.toml
COPY requirements-bot.txt requirements-bot.txt
COPY src src

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev build-essential \
    && python -m pip install --upgrade pip setuptools wheel \
    && pip install . \
    && pip install -r requirements-bot.txt \
    && apt-get remove -y gcc build-essential \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONPATH=/app/src

CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8000"]
