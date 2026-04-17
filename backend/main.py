from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.trends import router as trends_router
from database import engine, Base
import models.schema  # 모든 모델 import (테이블 생성용)

# Supabase에 테이블 자동 생성 (이미 있으면 스킵)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="TrendRadar API",
    description="한국 소비 트렌드 분석 플랫폼 백엔드",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(trends_router, prefix="/api/trends", tags=["trends"])


@app.get("/")
def root():
    return {"message": "TrendRadar API 서버 정상 작동 중 🚀"}


@app.get("/health")
def health():
    return {"status": "ok"}