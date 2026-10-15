from typing import Annotated

from fastapi import FastAPI, HTTPException, Request, status, Depends

from sqlalchemy import select
from sqlalchemy.orm import session

import models
from database import Base, engine, get_db

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def home():
    return {"message": "hello world"}

@app.get("/health")
async def health():
    return {"status": "ready"}