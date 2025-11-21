from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from backend.core.database import get_db
from sqlalchemy import func
from backend.schemas.weather import WeatherOut
from backend.models.weather import Weather
from backend.services.weather_service import fetch_current_weather, save_weather_record

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok"}


@router.post("/weather/fetch", response_model=WeatherOut)
def fetch_and_store_weather(
    lat: float = Query(None),
    lon: float = Query(None),
    db: Session = Depends(get_db),
):
    t, w, la, lo = fetch_current_weather(lat, lon)
    rec = save_weather_record(db, t, w, la, lo)
    return rec


@router.get("/weather", response_model=list[WeatherOut])
def list_weather(limit: int = 50, db: Session = Depends(get_db)):
    q = db.query(Weather).order_by(Weather.id.desc()).limit(limit).all()
    return list(reversed(q))  # időrendbe

@router.get("/weather/stats")
def get_weather_stats(db: Session = Depends(get_db)):
    q = db.query(
        func.count(Weather.id).label("count"),
        func.avg(Weather.temperature_c).label("avg_temp"),
        func.min(Weather.temperature_c).label("min_temp"),
        func.max(Weather.temperature_c).label("max_temp"),
        func.avg(Weather.windspeed_kmh).label("avg_wind"),
    ).one()

    return {
        "count": q.count,
        "avg_temp": round(q.avg_temp or 0, 2),
        "min_temp": round(q.min_temp or 0, 2),
        "max_temp": round(q.max_temp or 0, 2),
        "avg_wind": round(q.avg_wind or 0, 2),
    }

@router.get("/weather/{weather_id}", response_model=WeatherOut)
def get_weather_detail(weather_id: int, db: Session = Depends(get_db)):
    rec = db.query(Weather).filter(Weather.id == weather_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Record not found")
    return rec

@router.delete("/weather/reset")
def reset_database(db: Session = Depends(get_db)):
    """Delete all weather records from the database"""
    count = db.query(Weather).count()
    db.query(Weather).delete()
    db.commit()
    return {"message": f"Database reset successfully. Deleted {count} records."}