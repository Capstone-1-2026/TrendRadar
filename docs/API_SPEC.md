# API_SPEC.md — TrendRadar Backend API

베이스 URL: `/api/trends` (FastAPI, `backend/api/trends.py`)

> ⚠️ 현재 모든 엔드포인트는 `backend/api/trends.py` 내 하드코딩된 mock 데이터를 반환합니다.
> DB(Supabase) 연동 시 이 문서의 응답 스키마(shape)는 유지한 채 데이터 소스만 교체해야 합니다.
> (프론트엔드 `frontend/src/data/*.js` 목업도 같은 shape을 따르고 있으므로, 스펙 변경 시 프론트와 반드시 동기화)

---

## 1. GET `/api/trends/realtime`

현재 뜨고 있는 키워드 목록. 최신 수집 스냅샷 기준 `change_rate` 내림차순.

**응답**: `RealtimeItem[]`

```json
[
  {
    "id": 201,
    "name": "러닝크루",
    "cat": "lifestyle",
    "score": 89,
    "change_rate": 42.5,
    "collected_at": "2026-09-15T09:00:00+09:00"
  }
]
```

| 필드 | 타입   | 설명                                                                                                     |
| ---- | ------ | -------------------------------------------------------------------------------------------------------- |
| id   | int    | 키워드 ID                                                                                                |
| name | string | 키워드명                                                                                                 |
| cat  | string | 카테고리 (`food`, `fashion`, `content`, `technology`, `lifestyle`) — `snack`/`drink`는 `food`로 정규화됨 |
| score | int | 현재 트렌드 스코어 |
| change_rate | float | 직전 비교 구간 대비 변화율(%) |
| collected_at | string | 최신 수집 시각 |

> `RealtimeItem`은 `peak`/`year`(과거 최고점 필드)를 포함하지 않습니다. History 페이지의 `HistoryItem`(peak/year 기반)과 의도적으로 분리되어 있으며, 과거 종료된 키워드가 "현재" 화면에 peak 값으로 노출되는 것을 막기 위한 구조입니다.

---

## 2. GET `/api/trends/cycle`

현재 트렌드 타임라인 차트 + 워드클라우드용 월별 시계열.

**응답**: `CycleResponse`

```json
{
  "keywords": [
    /* KeywordItem[] */
  ],
  "series": [{ "label": "2021.01", "탕후루": 0, "마라탕": 12, "...": "..." }]
}
```

| 필드     | 타입          | 설명                                           |
| -------- | ------------- | ---------------------------------------------- |
| keywords | KeywordItem[] | 전체 키워드 목록                               |
| series   | dict[]        | 월별 row. `label`(YYYY.MM) + 키워드명별 스코어 |

---

## 3. GET `/api/trends/history`

과거 유행 키워드 히스토리 페이지용. 카테고리/연도 필터 + 하락 원인/하락률/AI 요약 포함.

**쿼리 파라미터**
| 이름 | 타입 | 필수 | 설명 |
|---|---|---|---|
| cat | string | X | `food`, `fashion`, `content`, `technology`, `lifestyle` 중 하나 |
| year | int | X | 연도 필터 (예: 2022) |

**응답**: `HistoryItem[]`

```json
[
  {
    "id": 5,
    "name": "탕후루",
    "cat": "food",
    "peak": 97,
    "year": 2022,
    "decline_cause": "자연 소멸",
    "drop_rate": 23,
    "summary": "탕후루은(는) 2022년 음식 카테고리에서 최고 스코어 97점을 기록했습니다. 이후 자연 소멸 원인으로 23% 하락세를 보였습니다."
  }
]
```

- `decline_cause`: 5가지 중 하나 — `대체재 등장`, `계절 종료`, `공급 과잉`, `부정 이슈`, `자연 소멸`

---

## 4. GET `/api/trends/predict`

다음 트렌드 후보 예측 페이지용. 예측 확률(prob) 내림차순.

**응답**: `PredictItem[]`

```json
[
  {
    "id": 101,
    "name": "단백질 디저트",
    "cat": "food",
    "prob": 84,
    "score": 82,
    "analysis": "..."
  }
]
```

> | 필드 | 타입 | 설명 |
> |---|---|---|
> | prob | int | 유행 가능성 % |
> | score | int | 예측 트렌드 스코어 |
> | analysis | string | AI 분석 텍스트 |

---

## 5. GET `/api/trends/decline`

히스토리 페이지 카테고리 요약 카드용. 카테고리별 평균 스코어/키워드 수.

**응답**: `DeclineItem[]`

```json
[{ "cat": "food", "label": "음식", "avg": 91.2, "count": 6 }]
```

> `food` 카테고리는 `snack`/`drink`가 정규화되어 합쳐지므로 count가 6, avg가 91.2가 됩니다(코드 기준 실측치).

---

## 공통 사항

- CORS 허용 origin: `http://localhost:5173` (Vite 기본 포트) — 배포 시 Vercel 도메인 추가 필요
- 새 엔드포인트 추가 시: ① `backend/models/schema.py`에 응답 모델 정의 → ② `backend/api/trends.py`에 라우터 구현 → ③ 이 문서 업데이트
