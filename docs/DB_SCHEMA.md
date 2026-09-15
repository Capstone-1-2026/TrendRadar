# DB_SCHEMA.md — TrendRadar Supabase Schema

원본 ERD: `/TrendRader_erd.png`

> ⚠️ 이 스키마는 설계 단계이며, 현재 백엔드는 이 테이블에 아직 연결되어 있지 않습니다
> (`backend/api/trends.py`는 하드코딩 mock 데이터 사용 중). DB 연동 작업 시 이 문서 기준으로 진행하고,
> 실제 컬럼을 바꾸게 되면 ERD 이미지도 함께 갱신해야 합니다.

---

## trend_keywords (마스터 테이블)

키워드 자체의 정보. 다른 모든 테이블이 `keyword_id`로 이 테이블을 참조.

| 컬럼          | 타입      | 필수 | 설명                                                                         |
| ------------- | --------- | ---- | ---------------------------------------------------------------------------- |
| id 🔑         | integer   | ✅   | PK                                                                           |
| name          | varchar   | ✅   | 키워드명 — **UNIQUE** (`data/pipeline.py`가 `on_conflict="name"`으로 upsert) |
| category      | varchar   | ✅   | 카테고리                                                                     |
| origin        | varchar   |      | 발생 출처                                                                    |
| trigger       | varchar   |      | 발생 트리거                                                                  |
| first_seen_at | date      |      | 최초 감지일                                                                  |
| created_at    | timestamp |      |                                                                              |
| updated_at    | timestamp |      |                                                                              |

---

## collection_logs (수집 로그)

데이터 수집 파이프라인 실행 이력. `trend_keywords`와 직접 FK 연결 없음(수집 배치 단위 로그).

| 컬럼          | 타입      | 필수 | 설명                                |
| ------------- | --------- | ---- | ----------------------------------- |
| id 🔑         | integer   | ✅   | PK                                  |
| collected_at  | timestamp | ✅   | 수집 실행 시각                      |
| source        | varchar   | ✅   | 수집 소스 (naver/youtube/google 등) |
| status        | varchar   | ✅   | 성공/실패 상태                      |
| keyword_count | integer   |      | 수집된 키워드 수                    |
| api_calls     | integer   |      | 소모한 API 호출 수                  |
| error_message | text      |      | 실패 시 에러 내용                   |
| created_at    | timestamp |      |                                     |

---

## trend_history (트렌드 이력)

키워드별 일/월 단위 스코어 이력. `docs/API_SPEC.md`의 `/cycle`, `/history` 응답의 원천 데이터.

| 컬럼            | 타입      | 필수 | 설명                                                                                                                                                                                 |
| --------------- | --------- | ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| id 🔑           | integer   | ✅   | PK                                                                                                                                                                                   |
| keyword_id 🔗   | integer   | ✅   | FK → trend_keywords.id                                                                                                                                                               |
| date            | date      | ✅   |                                                                                                                                                                                      |
| year            | integer   | ✅   |                                                                                                                                                                                      |
| month           | integer   | ✅   |                                                                                                                                                                                      |
| season          | varchar   |      |                                                                                                                                                                                      |
| naver_score     | float     |      | 네이버 DataLab 지수                                                                                                                                                                  |
| youtube_score   | float     |      | YouTube 조회/언급량                                                                                                                                                                  |
| google_score    | float     |      | Google Trends 지수                                                                                                                                                                   |
| trend_score     | float     |      | 최종 합산 스코어 (README 산식 참고)                                                                                                                                                  |
| cycle_stage     | varchar   |      | `emerging`/`growing`(또는 `growth`)/`peak`/`declining`/`revival`/`unknown` — 실제 코드값(영문). README의 발아/성장/피크/하락/부활은 이 값에 대응하는 한글 라벨일 뿐 DB 저장값이 아님 |
| lifecycle_month | integer   |      | 사이클 내 경과 개월                                                                                                                                                                  |
| created_at      | timestamp |      |                                                                                                                                                                                      |

**UNIQUE**: `(keyword_id, date)` — `data/pipeline.py`가 `on_conflict="keyword_id,date"`로 upsert

---

## trend_realtime (실시간 스냅샷)

`/api/trends/realtime` 응답의 원천 데이터. 최신 상태 스냅샷.

| 컬럼          | 타입      | 필수 | 설명                   |
| ------------- | --------- | ---- | ---------------------- |
| id 🔑         | integer   | ✅   | PK                     |
| keyword_id 🔗 | integer   | ✅   | FK → trend_keywords.id |
| collected_at  | timestamp | ✅   |                        |
| naver_score   | float     |      |                        |
| youtube_score | float     |      |                        |
| trend_score   | float     |      |                        |
| change_rate   | float     |      | 전월 대비 증감률       |
| cycle_stage   | varchar   |      |                        |
| created_at    | timestamp |      |                        |

---

## trend_predictions (AI 예측)

`/api/trends/predict` 응답의 원천 데이터.

| 컬럼               | 타입      | 필수 | 설명                    |
| ------------------ | --------- | ---- | ----------------------- |
| id 🔑              | integer   | ✅   | PK                      |
| keyword_id 🔗      | integer   | ✅   | FK → trend_keywords.id  |
| predicted_at       | date      | ✅   | 예측 실행일             |
| prob               | float     |      | 유행 가능성 %           |
| trend_score        | float     |      |                         |
| peak_expected      | date      |      | 예상 피크 시점          |
| lifecycle_expected | integer   |      | 예상 사이클 개월 수     |
| revival_prob       | float     |      | 부활 가능성             |
| model_version      | varchar   |      | 예측에 사용된 모델 버전 |
| created_at         | timestamp |      |                         |

**UNIQUE**: `(keyword_id, predicted_at)` — `data/collectors/predictor.py`가 `on_conflict="keyword_id,predicted_at"`로 upsert

---

## decline_events (하락 이벤트)

`/api/trends/history`의 `decline_cause`, `drop_rate` 원천 데이터.

| 컬럼            | 타입      | 필수 | 설명                                                        |
| --------------- | --------- | ---- | ----------------------------------------------------------- |
| id 🔑           | integer   | ✅   | PK                                                          |
| keyword_id 🔗   | integer   | ✅   | FK → trend_keywords.id                                      |
| detected_at     | date      | ✅   | 하락 감지일                                                 |
| decline_rate    | float     |      | 하락률                                                      |
| cause_type      | varchar   |      | 대체재 등장 / 계절 종료 / 공급 과잉 / 부정 이슈 / 자연 소멸 |
| cause_detail    | text      |      | 상세 설명                                                   |
| related_keyword | varchar   |      | 대체재 등장 시 관련 키워드                                  |
| resolved_at     | date      |      | 하락 이후 안정화/부활 시점                                  |
| created_at      | timestamp |      |                                                             |

---

## seasonal_patterns (계절 패턴)

Trend Score 계산 시 계절 보정 계수(×0.2)의 원천 데이터.

| 컬럼          | 타입      | 필수 | 설명                   |
| ------------- | --------- | ---- | ---------------------- |
| id 🔑         | integer   | ✅   | PK                     |
| keyword_id 🔗 | integer   | ✅   | FK → trend_keywords.id |
| season        | varchar   | ✅   | 봄/여름/가을/겨울 등   |
| month         | integer   |      |                        |
| avg_score     | float     |      | 해당 시즌 평균 스코어  |
| peak_month    | integer   |      | 시즌 내 피크 월        |
| recurrence    | varchar   |      | 매년 반복 여부/패턴    |
| created_at    | timestamp |      |                        |

---

## 관계 요약

`trend_keywords.id`를 다음 5개 테이블이 `keyword_id`로 참조 (1:N):
`trend_history`, `trend_realtime`, `trend_predictions`, `decline_events`, `seasonal_patterns`
(`collection_logs`는 독립 테이블, FK 없음)

## Unique 제약 요약 (실제 upsert 코드 기준)

| 테이블            | UNIQUE 컬럼                | 근거                                                                  |
| ----------------- | -------------------------- | --------------------------------------------------------------------- |
| trend_keywords    | name                       | `data/pipeline.py: on_conflict="name"`                                |
| trend_history     | (keyword_id, date)         | `data/pipeline.py: on_conflict="keyword_id,date"`                     |
| trend_predictions | (keyword_id, predicted_at) | `data/collectors/predictor.py: on_conflict="keyword_id,predicted_at"` |

## 구현 진행 상태

- `data/pipeline.py`, `data/collectors/*`: `trend_keywords`, `trend_history`, `trend_predictions` upsert 로직 **구현됨**
- `backend/api/trends.py`: 위 테이블을 아직 **조회하지 않음** — 하드코딩 mock 반환 중 (API_SPEC.md 참고)

## 백엔드 연동 시 매핑 참고

| API 응답 (API_SPEC.md)        | 원천 테이블                              |
| ----------------------------- | ---------------------------------------- |
| `/realtime` → `KeywordItem[]` | `trend_keywords` + `trend_realtime` join |
| `/cycle` → `CycleResponse`    | `trend_history`                          |
| `/history` → `HistoryItem[]`  | `trend_keywords` + `decline_events` join |
| `/predict` → `PredictItem[]`  | `trend_predictions`                      |
| `/decline` → `DeclineItem[]`  | `trend_keywords` + `trend_history` 집계  |
