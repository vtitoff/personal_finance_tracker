from contextlib import asynccontextmanager

import uvicorn
from api.v1.payment_categories import router as categories_router
from api.v1.payment_methods import router as payment_methods_router
from api.v1.users import router as users_router
from core.config import settings
from db import postgres
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi_pagination import add_pagination
from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)


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

app.include_router(categories_router, prefix="/api/v1", tags=["categories"])
app.include_router(payment_methods_router, prefix="/api/v1", tags=["payment_methods"])
app.include_router(users_router, prefix="/api/v1", tags=["users"])

add_pagination(app)

if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8080, reload=True)
