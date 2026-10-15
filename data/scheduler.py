# /Users/apple/TrendRadar/data/scheduler.py

import logging
import os
from datetime import datetime
from dotenv import load_dotenv
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from pipeline import run_pipeline
from realtime_pipeline import run_realtime_pipeline

load_dotenv()

COLLECTION_HOUR = int(os.getenv("COLLECTION_HOUR", "2"))
COLLECTION_MINUTE = int(os.getenv("COLLECTION_MINUTE", "0"))
REALTIME_INTERVAL_MINUTES = int(os.getenv("REALTIME_INTERVAL_MINUTES", "30"))

# ─────────────────────────────────────────
# 로깅 설정
# ─────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("scheduler.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


# ─────────────────────────────────────────
# 수집 작업
# ─────────────────────────────────────────
def job_collect_trends():
    """TrendRadar 전체 트렌드 수집 + Supabase 적재"""
    logger.info("=" * 50)
    logger.info(f"🚀 트렌드 수집 시작: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        run_pipeline()
        logger.info("✅ 트렌드 수집 파이프라인 완료")
    except Exception as e:
        logger.error(f"❌ 오류 발생: {e}", exc_info=True)

    logger.info("=" * 50)


def job_collect_realtime():
    """현재 트렌드 키워드 실시간 수집 + trend_realtime 적재"""
    logger.info("=" * 50)
    logger.info(f"⚡ 실시간 수집 시작: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        run_realtime_pipeline()
        logger.info("✅ 실시간 수집 완료")
    except Exception as e:
        logger.error(f"❌ 오류 발생: {e}", exc_info=True)

    logger.info("=" * 50)


# ─────────────────────────────────────────
# 스케줄러 설정
# ─────────────────────────────────────────
def main():
    scheduler = BlockingScheduler(timezone="Asia/Seoul")

    scheduler.add_job(
        job_collect_trends,
        trigger=CronTrigger(hour=COLLECTION_HOUR, minute=COLLECTION_MINUTE),
        id="trend_collection_daily",
        name="TrendRadar 일일 트렌드 수집",
        max_instances=1,  # 중복 실행 방지
        misfire_grace_time=300,  # 5분 이내 지연 허용
    )

    scheduler.add_job(
        job_collect_realtime,
        trigger=IntervalTrigger(minutes=REALTIME_INTERVAL_MINUTES),
        id="trend_collection_realtime",
        name="TrendRadar 실시간 트렌드 수집",
        max_instances=1,
        misfire_grace_time=120,
        next_run_time=datetime.now(),  # 시작 즉시 1회 실행
    )

    logger.info("📅 스케줄러 시작")
    logger.info(f"  └─ 매일 {COLLECTION_HOUR:02d}:{COLLECTION_MINUTE:02d} 히스토리 트렌드 수집")
    logger.info(f"  └─ {REALTIME_INTERVAL_MINUTES}분마다 실시간 트렌드 수집")
    logger.info("  └─ 종료하려면 Ctrl+C")

    try:
        scheduler.start()
    except KeyboardInterrupt:
        logger.info("🛑 스케줄러 종료")
        scheduler.shutdown()


if __name__ == "__main__":
    main()
