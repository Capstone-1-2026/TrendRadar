# 🎯 TrendRadar — 한국 트렌드 예측 플랫폼

> AI 기반 한국 시장 특화 트렌드 예측 및 하락 원인 분석 플랫폼

---

## 📌 프로젝트 개요

| 항목 | 내용 |
|------|------|
| **프로젝트명** | TrendRadar |
| **목적** | 한국 시장 데이터 기반 트렌드 예측 및 하락 원인 분석 |
| **타겟** | 소상공인 / 크리에이터 / 창업가 |
| **개발 기간** | 2026.03 ~ |
| **팀 구성** | 4명 (기획 / 프론트 / 백엔드 / DB) |

---

## ✨ 핵심 기능

### 1️⃣ 미래 트렌드 예측
- 과거 5~10년 데이터 + 실시간 수집 데이터 결합
- 계절/시기별 패턴 분석 (한국 특화 이벤트 반영)
- Trend Cycle 단계별 분류 (발아 → 성장 → 피크 → 하락 → 부활)
- AI 기반 유행 가능성 % 예측

### 2️⃣ 하락 원인 분석
- 하락세 키워드 자동 감지
- 원인 유형 자동 분류
  - 대체재 등장 / 계절 종료 / 공급 과잉 / 부정 이슈 / 자연 소멸
- 유사 과거 사례 비교 제공

---

## 🛠️ 기술 스택

### 프론트엔드
| 기술 | 용도 |
|------|------|
| React 18 | UI 프레임워크 |
| Vite | 빌드 도구 |
| Recharts | 데이터 시각화 |
| React Router | 페이지 라우팅 |

### 백엔드
| 기술 | 용도 |
|------|------|
| FastAPI | REST API 서버 |
| Python 3.11 | 데이터 수집 및 처리 |
| SQLAlchemy | ORM |

### 데이터베이스
| 기술 | 용도 |
|------|------|
| Supabase (PostgreSQL) | 메인 DB |

### 데이터 수집
| 기술 | 용도 |
|------|------|
| 네이버 DataLab API | 한국 검색 트렌드 (일 1,000회) |
| YouTube Data API | KR 콘텐츠 트렌드 (일 10,000 유닛) |
| pytrends | Google Trends 수집 |
| pandas / numpy | 데이터 처리 |
| APScheduler | 매일 새벽 2시 자동 수집 |

### 배포
| 서비스 | 용도 |
|--------|------|
| Vercel | 프론트엔드 |
| Render | 백엔드 |

---

## 📁 프로젝트 구조
```
TrendRadar/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── common/       # 공통 컴포넌트
│   │   │   ├── icons/        # SVG 아이콘
│   │   │   └── layout/       # 레이아웃 (Sidebar, Header)
│   │   ├── context/          # ThemeContext
│   │   ├── data/             # 목업 데이터
│   │   ├── hooks/            # 커스텀 훅
│   │   ├── pages/            # 페이지 컴포넌트
│   │   │   ├── Dashboard.jsx
│   │   │   ├── History.jsx
│   │   │   └── AIPrediction.jsx
│   │   └── theme/            # 디자인 토큰
│   └── package.json
├── backend/                  # FastAPI (구축 예정)
├── data/                     # 데이터 수집 파이프라인 (구축 예정)
└── docs/                     # 기획 문서
```

---

## 🌿 브랜치 전략
```
main
└── dev
    ├── feature/frontend-xxx   ← 프론트 담당
    ├── feature/backend-xxx    ← 백엔드 담당
    └── feature/data-xxx       ← DB 담당
```

| 규칙 | 내용 |
|------|------|
| `main` 직접 push | ❌ 금지 |
| 작업 단위 | 각자 feature 브랜치 |
| merge 방식 | PR → 팀장 리뷰 → dev merge |
| `dev → main` | 최종 완성본만 |

---

## 👥 팀 역할 분담

| 역할 | 담당 작업 |
|------|----------|
| 기획 / 팀장 | 설계 · 디버깅 · 코드리뷰 · merge 승인 |
| 프론트엔드 | React 컴포넌트 · UI 구현 |
| 백엔드 | FastAPI 서버 · API 라우터 |
| DB / 데이터 | 수집 파이프라인 · Supabase 설계 · AI 모델 |

---

## 📊 Trend Score 산식
```
Trend Score =
  (네이버 DataLab 검색 지수 × 0.5)
+ (YouTube 조회/언급량 × 0.3)
+ (계절 보정 계수 × 0.2)

※ 네이버 지표는 상대값(최대 = 100) 기준
※ 모든 소스 정규화 후 합산
```

---

## 🔄 Trend Cycle 단계

| 단계 | 기준 |
|------|------|
| 발아 | Trend Score 20 미만 + 전월 대비 +10% 이상 |
| 성장 | Trend Score 20~60 + 전월 대비 +20% 이상 |
| 피크 | Trend Score 60 이상 + 증가율 둔화 |
| 하락 | 전월 대비 -15% 이상 |
| 부활 | 하락 후 6개월+ 경과 + 다시 +10% 이상 |

---

## 🚀 로컬 실행 방법
```bash
# 레포 클론
git clone https://github.com/조직이름/TrendRadar.git
cd TrendRadar

# 패키지 설치
pnpm install

# 개발 서버 실행
pnpm run dev
```

---

## 📅 개발 로드맵

| 단계 | 내용 | 상태 |
|------|------|------|
| Phase 0 | 사전 준비 · 기술스택 확정 | ✅ 완료 |
| Phase 1 | 프론트엔드 구현 · Vite 전환 | ✅ 완료 |
| Phase 2 | 데이터 수집 파이프라인 | 🔜 진행 예정 |
| Phase 3 | FastAPI 백엔드 구축 | 🔜 진행 예정 |
| Phase 4 | AI 예측 모델 연동 | 🔜 진행 예정 |
| Phase 5 | 통합 테스트 · 배포 | 🔜 진행 예정 |
