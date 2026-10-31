from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, APIRouter, HTTPException, Request, status, Depends

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import session

from app import models
#from config import settings
from app.database import engine
from app.auth.router import router as router_auth
from app.notification.router import router as router_notification

@asynccontextmanager
async def lifespan(_app: FastAPI):
    yield
    #shoutdown
    await engine.dispose()

#router = APIRouter()
app = FastAPI(lifespan=lifespan)

@app.get("/health")
async def health():
    return {"status": "ready"}

app.include_router(router_auth)
app.include_router(router_notification)