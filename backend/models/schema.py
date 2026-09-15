from sqlalchemy import (
    Column, Integer, String, Float, Date,
    DateTime, Text, ForeignKey, func
)
from sqlalchemy.orm import relationship
from database import Base
from pydantic import BaseModel


# ── SQLAlchemy DB 테이블 모델 ──────────────────────────────────

class TrendKeyword(Base):
    __tablename__ = "trend_keywords"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    category = Column(String, nullable=False)
    origin = Column(String)
    trigger = Column(String)
    first_seen_at = Column(Date)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # 관계 설정
    history = relationship("TrendHistory", back_populates="keyword")
    realtime = relationship("TrendRealtime", back_populates="keyword")
    predictions = relationship("TrendPrediction", back_populates="keyword")
    decline_events = relationship("DeclineEvent", back_populates="keyword")
    seasonal_patterns = relationship("SeasonalPattern", back_populates="keyword")


class TrendHistory(Base):
    __tablename__ = "trend_history"

    id = Column(Integer, primary_key=True, index=True)
    keyword_id = Column(Integer, ForeignKey("trend_keywords.id"), nullable=False)
    date = Column(Date, nullable=False)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    season = Column(String)
    naver_score = Column(Float)
    youtube_score = Column(Float)
    google_score = Column(Float)
    trend_score = Column(Float)
    cycle_stage = Column(String)
    lifecycle_month = Column(Integer)
    created_at = Column(DateTime, server_default=func.now())

    keyword = relationship("TrendKeyword", back_populates="history")


class TrendRealtime(Base):
    __tablename__ = "trend_realtime"

    id = Column(Integer, primary_key=True, index=True)
    keyword_id = Column(Integer, ForeignKey("trend_keywords.id"), nullable=False)
    collected_at = Column(DateTime, server_default=func.now())
    naver_score = Column(Float)
    youtube_score = Column(Float)
    trend_score = Column(Float)
    change_rate = Column(Float)
    cycle_stage = Column(String)
    created_at = Column(DateTime, server_default=func.now())

    keyword = relationship("TrendKeyword", back_populates="realtime")


class TrendPrediction(Base):
    __tablename__ = "trend_predictions"

    id = Column(Integer, primary_key=True, index=True)
    keyword_id = Column(Integer, ForeignKey("trend_keywords.id"), nullable=False)
    predicted_at = Column(Date, nullable=False)
    prob = Column(Float)
    trend_score = Column(Float)
    peak_expected = Column(Date)
    lifecycle_expected = Column(Integer)
    revival_prob = Column(Float)
    model_version = Column(String)
    created_at = Column(DateTime, server_default=func.now())

    keyword = relationship("TrendKeyword", back_populates="predictions")


class DeclineEvent(Base):
    __tablename__ = "decline_events"

    id = Column(Integer, primary_key=True, index=True)
    keyword_id = Column(Integer, ForeignKey("trend_keywords.id"), nullable=False)
    detected_at = Column(Date, nullable=False)
    decline_rate = Column(Float)
    cause_type = Column(String)
    cause_detail = Column(Text)
    related_keyword = Column(String)
    resolved_at = Column(Date)
    created_at = Column(DateTime, server_default=func.now())

    keyword = relationship("TrendKeyword", back_populates="decline_events")


class SeasonalPattern(Base):
    __tablename__ = "seasonal_patterns"

    id = Column(Integer, primary_key=True, index=True)
    keyword_id = Column(Integer, ForeignKey("trend_keywords.id"), nullable=False)
    season = Column(String, nullable=False)
    month = Column(Integer)
    avg_score = Column(Float)
    peak_month = Column(Integer)
    recurrence = Column(String)
    created_at = Column(DateTime, server_default=func.now())

    keyword = relationship("TrendKeyword", back_populates="seasonal_patterns")


class CollectionLog(Base):
    __tablename__ = "collection_logs"

    id = Column(Integer, primary_key=True, index=True)
    collected_at = Column(DateTime, server_default=func.now())
    source = Column(String, nullable=False)
    status = Column(String, nullable=False)
    keyword_count = Column(Integer)
    api_calls = Column(Integer)
    error_message = Column(Text)
    created_at = Column(DateTime, server_default=func.now())


# ── Pydantic 응답 모델 ─────────────────────────────────────────

class KeywordItem(BaseModel):
    id: int
    name: str
    cat: str
    peak: int
    year: int

class CycleResponse(BaseModel):
    keywords: list[KeywordItem]
    series: list[dict]

class HistoryItem(BaseModel):
    id: int
    name: str
    cat: str
    peak: int
    year: int
    decline_cause: str
    drop_rate: int
    summary: str

class PredictItem(BaseModel):
    id: int
    name: str
    cat: str
    prob: int
    score: int
    analysis: str

class DeclineItem(BaseModel):
    cat: str
    label: str
    avg: float
    count: int