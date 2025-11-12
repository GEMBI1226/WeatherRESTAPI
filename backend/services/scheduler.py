from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from backend.core.database import SessionLocal
from backend.core.config import settings
from backend.core.logging_conf import logger
from backend.services.weather_service import fetch_current_weather, save_weather_record

scheduler: BackgroundScheduler | None = None


def _job():
    logger.info("Scheduler tick: fetching weather…")
    db: Session = SessionLocal()
    try:
        t, w, lat, lon = fetch_current_weather()
        save_weather_record(db, t, w, lat, lon)
        logger.info("Weather saved.")
    except Exception as e:
        logger.exception("Scheduled job failed: %s", e)
    finally:
        db.close()


def start_scheduler():
    global scheduler
    if not settings.scheduler_enabled:
        logger.info("Scheduler disabled by config.")
        return
    scheduler = BackgroundScheduler()
    scheduler.add_job(_job, "interval", minutes=settings.scheduler_interval_min, id="weather_job", replace_existing=True)
    scheduler.start()
    logger.info("Scheduler started (interval=%s min)", settings.scheduler_interval_min)


def stop_scheduler():
    global scheduler
    if scheduler:
        scheduler.shutdown(wait=False)
        scheduler = None