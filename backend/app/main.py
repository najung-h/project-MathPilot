"""FastAPI Application Entry Point"""

from contextlib import asynccontextmanager
import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import video, note
from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    # Startup
    # 스토리지 디렉토리 생성
    os.makedirs(settings.STORAGE_PATH, exist_ok=True)
    yield
    # Shutdown


app = FastAPI(
    title="MathNote API",
    description="강의 영상을 분석하여 수식이 포함된 단권화 노트를 자동 생성하는 API",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 파일 서빙 (로컬 스토리지용)
app.mount("/static", StaticFiles(directory=settings.STORAGE_PATH), name="static")

# 라우터 등록
app.include_router(video.router, prefix="/api/v1/videos", tags=["videos"])
app.include_router(note.router, prefix="/api/v1/notes", tags=["notes"])


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
