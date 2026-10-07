from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import GENERATED_CERTIFICATES_DIR
from app.database import Base, engine
from app.routers.certificates import (
    router as certificates_router,
)
from app.routers.jobs import router as jobs_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)

    GENERATED_CERTIFICATES_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    yield


app = FastAPI(
    title="CertiFlow API",
    description=(
        "Bulk Certificate Generation and Verification API "
        "for the Aereo SDE Intern assignment."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


app.include_router(jobs_router)
app.include_router(certificates_router)


@app.get(
    "/health",
    tags=["System"],
)
def health_check():
    return {
        "status": "healthy",
        "service": "CertiFlow API",
        "version": "1.0.0",
    }
