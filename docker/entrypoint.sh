#!/bin/sh
set -e

echo "Ожидание готовности БД..."
python - <<'PY'
import asyncio
import os

import asyncpg

dsn = os.environ.get("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@db:5432/postgres").replace(
    "+asyncpg", ""
)


async def wait_for_db() -> None:
    while True:
        try:
            conn = await asyncpg.connect(dsn)
            await conn.close()
            print("База данных доступна.")
            return
        except Exception as exc:  # noqa: BLE001
            print(f"База данных недоступна: {exc}")
            await asyncio.sleep(2)


asyncio.run(wait_for_db())
PY

echo "Запуск миграций..."
alembic upgrade head

echo "Старт приложения..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000

