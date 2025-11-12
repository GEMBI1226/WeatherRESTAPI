import requests
from sqlalchemy.orm import Session
from backend.models.weather import Weather
from backend.core.config import settings
from backend.core.logging_conf import logger

OPEN_METEO_URL = (
    "https://api.open-meteo.com/v1/forecast?current=temperature_2m,wind_speed_10m&latitude={lat}&longitude={lon}"
)


def fetch_current_weather(lat: float | None = None, lon: float | None = None) -> tuple[float, float, float, float]:
    lat = lat or settings.default_lat
    lon = lon or settings.default_lon
    url = OPEN_METEO_URL.format(lat=lat, lon=lon)
    logger.info(f"Fetching weather from Open-Meteo: {url}")
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    data = r.json()
    temp = data["current"]["temperature_2m"]
    wind = data["current"]["wind_speed_10m"]
    return float(temp), float(wind), float(lat), float(lon)


def save_weather_record(db: Session, temp_c: float, wind_kmh: float, lat: float, lon: float) -> Weather:
    rec = Weather(temperature_c=temp_c, windspeed_kmh=wind_kmh, latitude=lat, longitude=lon)
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec