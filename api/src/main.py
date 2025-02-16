from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)

from core.config import settings
from db import postgres


@asynccontextmanager
async def lifespan(app: FastAPI):
    postgres.engine = create_async_engine(
        postgres.dsn, echo=settings.engine_echo, future=True
    )
    postgres.async_session = async_sessionmaker(bind=postgres.engine, expire_on_commit=False, class_=AsyncSession)  # type: ignore[assignment]
    yield


app = FastAPI(
    lifespan=lifespan,
    title=settings.project_name,
    docs_url="/api/openapi/",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
)


if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8080, reload=True)
