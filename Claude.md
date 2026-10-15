# CLAUDE.md — TrendRadar

이 파일은 Claude Code와 Codex CLI가 공통으로 참조하는 프로젝트 컨텍스트입니다.
(Codex CLI는 `AGENTS.md`를 읽습니다. 아직 심볼릭 링크가 실제로 생성되어 있지 않다면, 레포 루트에서
`ln -s CLAUDE.md AGENTS.md`를 먼저 실행하세요.)

## 프로젝트 개요

- **이름**: TrendRadar — 한국 시장 특화 트렌드 예측 및 하락 원인 분석 플랫폼
- **팀**: 2인 (프론트엔드 담당 / 백엔드+데이터 담당)
- **현재 단계**: 프론트엔드는 목업 데이터로 UI 완성. 백엔드(FastAPI)는 하드코딩된 mock 데이터로 API 형태만 잡힌 상태(응답 스키마는 실제 DB 스키마와 아직 다름). 데이터 파이프라인(`data/`)은 Supabase upsert까지 구현되어 있어 백엔드보다 앞서 있는 상태.

## 기술 스택

| 영역        | 기술                                                                                      |
| ----------- | ----------------------------------------------------------------------------------------- |
| 프론트엔드  | React 19, Vite, Recharts — 라우팅 라이브러리 없이 `useState` 기반 페이지 전환 (`App.jsx`) |
| 백엔드      | FastAPI, Python 3.11, Pydantic                                                            |
| DB          | Supabase (PostgreSQL) — 스키마는 설계/일부 구현됨, `backend`는 아직 미연동(mock 사용 중)  |
| 데이터 수집 | 네이버 DataLab API, YouTube Data API, pytrends, pandas, APScheduler                       |
| 배포        | Vercel(프론트) / Render(백엔드)                                                           |

## 디렉토리 구조

```
TrendRadar/
├── frontend/src/{components,context,data,hooks,pages,theme}/
├── backend/{api,models}/     # api/trends.py, models/schema.py
├── data/{collectors,pipeline.py,scheduler.py}/
└── docs/
    ├── API_SPEC.md           # /api/trends/* 엔드포인트 상세
    └── DB_SCHEMA.md           # Supabase 테이블 설계
```

## 실행 명령어

```bash
# 프론트엔드
cd frontend && pnpm install && pnpm run dev

# 백엔드
cd backend && pip install -r requirements.txt && uvicorn main:app --reload

# 데이터 파이프라인
cd data && pip install -r requirements.txt && python pipeline.py
```

## 작업 시 참고할 문서

- API 엔드포인트를 추가/수정할 때 → `docs/API_SPEC.md` 먼저 확인하고 작업 후 반드시 업데이트
- DB 테이블 관련 작업(쿼리, ORM 모델 작성 등) → `docs/DB_SCHEMA.md` 먼저 확인
- 두 문서 모두 실제 코드와 어긋나면 안 됨 — 스키마나 API를 바꾸면 해당 md도 같이 수정할 것

## 코드 컨벤션

- **백엔드**: 라우터는 `backend/api/*.py`에 도메인별 분리, 응답 스키마는 `backend/models/schema.py`에 Pydantic 모델로 먼저 정의.
- **프론트엔드**: 페이지는 `pages/`, 재사용 컴포넌트는 `components/common/`. `src/data/*.js` 목업을 실제 API로 교체할 때 응답 shape 유지.
- **커밋 메시지**: `feat:`, `fix:`, `docs:`, `refactor:` 등 conventional commit 접두사.

## 하지 말아야 할 것

- `frontend/src/data/*.js` 목업 구조를 API 스펙과 맞추지 않고 임의로 바꾸지 말 것
- `.env` 파일이나 API 키를 커밋하지 말 것
- `backend/api/trends.py`의 하드코딩 데이터를 실제 DB 쿼리로 바꿀 때, `docs/DB_SCHEMA.md` 컬럼명과 다르게 임의 네이밍하지 말 것
