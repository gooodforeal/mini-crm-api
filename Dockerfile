FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*

# сначала ставим зависимости, чтобы слои кэшировались
COPY pyproject.toml README.md requirements.txt ./
COPY app ./app
RUN pip install --upgrade pip && pip install -r requirements.txt

# затем копируем остальные файлы проекта
COPY . .

RUN chmod +x docker/entrypoint.sh

EXPOSE 8000

CMD ["./docker/entrypoint.sh"]

