from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from backend.core.database import SessionLocal
from backend.core.config import settings
from backend.core.logging_conf import logger
from backend.services.weather_service import fetch_current_weather, save_weather_record
from backend.services.email_service import send_email

# ===== 5 város koordinátái =====
CITIES = [
    ("Budapest", 47.4979, 19.0402),
    ("Eger", 47.902534, 20.377228),
    ("Debrecen", 47.531605, 21.627312),
    ("Szeged", 46.253, 20.141),
    ("Pécs", 46.0727, 18.2323),
]

scheduler: BackgroundScheduler | None = None


def _job():
    logger.info("Scheduler tick: fetching weather for 5 cities…")
    db: Session = SessionLocal()

    try:
        report_lines = []

        for name, lat, lon in CITIES:
            # lekérés Open-Meteo-ból
            t, w, la, lo = fetch_current_weather(lat, lon)

            # mentés adatbázisba
            save_weather_record(db, t, w, la, lo)

            line = f"{name}: {t}°C, {w} km/h (Lat: {lat}, Lon: {lon})"
            report_lines.append(line)

            logger.info("Saved " + line)

        # ======= EMAIL KÜLDÉSE =======
        email_body = "Óránkénti időjárás riport:\n\n" + "\n".join(report_lines)
        send_email("Óránkénti időjárás jelentés", email_body)
        logger.info("Email értesítés elküldve.")

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
    scheduler.add_job(
        _job,
        "interval",
        minutes=settings.scheduler_interval_min,
        id="weather_job",
        replace_existing=True
    )
    scheduler.start()

    logger.info(f"Scheduler started (interval={settings.scheduler_interval_min} min)")


def stop_scheduler():
    global scheduler
    if scheduler:
        scheduler.shutdown(wait=False)
        scheduler = None
