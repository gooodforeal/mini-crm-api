from __future__ import annotations

import asyncio

import typer

from app.db.session import async_session_factory

app = typer.Typer()


@app.command()
def shell() -> None:
    """Простая консоль для отладки."""
    async def _shell() -> None:
        async with async_session_factory() as session:
            typer.echo(f"Сессия готова: {session}")

    asyncio.run(_shell())


