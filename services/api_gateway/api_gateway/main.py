from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from api_gateway.routes import webhook
from api_gateway.config import settings

from shared.providers.redis import RedisFactory
from shared.logging import setup_logging

import logging
setup_logging()
logger = logging.getLogger("API-Gateway.Main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up API Gateway...")
    RedisFactory.get_client(settings)  # Initialize Redis connection pool
    yield
    logger.info("Shutting down API Gateway...")
    await RedisFactory.close()

app = FastAPI(
    title="Git Sentinel API Gateway",
    version="1.0.0",
    description="API Gateway for the Git Sentinel application.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(webhook.router, prefix="/webhook", tags=["Webhook"])

@app.get("/", tags=["Root"])
async def root():
    return {"message": "Welcome to the Git Sentinel API Gateway!"}


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok"}
