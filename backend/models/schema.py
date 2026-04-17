from pydantic import BaseModel
from typing import Optional


# ── /api/trends/realtime ──────────────────────────────
class KeywordItem(BaseModel):
    id: int
    name: str
    cat: str
    peak: int
    year: int


# ── /api/trends/cycle ─────────────────────────────────
class CycleResponse(BaseModel):
    keywords: list[KeywordItem]
    series: list[dict]


# ── /api/trends/history ───────────────────────────────
class HistoryItem(BaseModel):
    id: int
    name: str
    cat: str
    peak: int
    year: int
    decline_cause: str
    drop_rate: int
    summary: str


# ── /api/trends/predict ───────────────────────────────
class PredictItem(BaseModel):
    id: int
    name: str
    cat: str
    prob: int
    score: int
    analysis: str


# ── /api/trends/decline ───────────────────────────────
class DeclineItem(BaseModel):
    cat: str
    label: str
    avg: float
    count: int