from backend.core.database import SessionLocal, Base, engine
from backend.services.weather_service import fetch_current_weather, save_weather_record

Base.metadata.create_all(bind=engine)

db = SessionLocal()
try:
    t, w, la, lo = fetch_current_weather()
    save_weather_record(db, t, w, la, lo)
    print("Seed kész.")
finally:
    db.close()