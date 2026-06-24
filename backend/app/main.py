from contextlib import asynccontextmanager
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.api.routes import jobs

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic can go here (e.g., initial test connections)
    yield
    # Shutdown logic can go here

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(jobs.router, prefix=settings.API_V1_STR)

os.makedirs("tmp", exist_ok=True)
app.mount("/media", StaticFiles(directory="tmp"), name="media")

@app.get("/health", response_class=JSONResponse)
async def health_check():
    """
    Basic health check endpoint.
    """
    return {"status": "healthy", "project": settings.PROJECT_NAME}
