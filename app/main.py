from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.auth.router import router as router_auth

# from config import settings
from app.database import engine
from app.notification.router import router as router_notification


@asynccontextmanager
async def lifespan(_app: FastAPI):
    yield
    # shoutdown
    await engine.dispose()


# router = APIRouter()
app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "ready"}


app.include_router(router_auth)
app.include_router(router_notification)
