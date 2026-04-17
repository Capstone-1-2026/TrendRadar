# /Users/apple/TrendRadar/data/scheduler.py

import logging
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from collectors.youtube import collect_youtube_trends, upload_to_supabase

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
def job_youtube():
    """YouTube 트렌드 수집 + Supabase 적재"""
    logger.info("=" * 50)
    logger.info(f"🚀 YouTube 수집 시작: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        df = collect_youtube_trends()

        if not df.empty:
            upload_to_supabase(df)
            logger.info(f"✅ 완료: {len(df)}개 영상 수집 및 적재")
        else:
            logger.warning("⚠️ 수집된 데이터 없음")

    except Exception as e:
        logger.error(f"❌ 오류 발생: {e}", exc_info=True)

    logger.info("=" * 50)


# ─────────────────────────────────────────
# 스케줄러 설정
# ─────────────────────────────────────────
def main():
    scheduler = BlockingScheduler(timezone="Asia/Seoul")

    # 오전 9시 수집
    scheduler.add_job(
        job_youtube,
        trigger=CronTrigger(hour=9, minute=0),
        id="youtube_morning",
        name="YouTube 오전 수집",
        max_instances=1,  # 중복 실행 방지
        misfire_grace_time=300,  # 5분 이내 지연 허용
    )

    # 오후 9시 수집
    scheduler.add_job(
        job_youtube,
        trigger=CronTrigger(hour=21, minute=0),
        id="youtube_evening",
        name="YouTube 오후 수집",
        max_instances=1,
        misfire_grace_time=300,
    )

    logger.info("📅 스케줄러 시작")
    logger.info("  └─ 오전 09:00 YouTube 수집")
    logger.info("  └─ 오후 21:00 YouTube 수집")
    logger.info("  └─ 종료하려면 Ctrl+C")

    # 시작 즉시 1회 실행 (테스트용)
    logger.info("⚡ 즉시 1회 테스트 실행...")
    job_youtube()

    try:
        scheduler.start()
    except KeyboardInterrupt:
        logger.info("🛑 스케줄러 종료")
        scheduler.shutdown()


if __name__ == "__main__":
    main()
