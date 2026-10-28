from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, HTTPException, Request, status, Depends

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import session

from app import models
#from config import settings
from app.database import engine, get_db
#from routers import posts

asynccontextmanager
async def lifespan(_app: FastAPI):
    yield
    #shoutdown
    await engine.dispose()

app = FastAPI(lifespan=lifespan)

@app.get("/")
def home():
    return {"message": "hello world"}

@app.get("/health")
async def health():
    return {"status": "ready"}