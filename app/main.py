from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.config import settings
from app.services import exceptions

app = FastAPI(title=settings.app_name, version="1.0.0")
app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.exception_handler(exceptions.ServiceError)
async def service_error_handler(request: Request, exc: exceptions.ServiceError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


