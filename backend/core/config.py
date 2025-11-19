from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseModel):
    app_env: str = os.getenv("APP_ENV", "dev")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./weather.db")
    default_lat: float = float(os.getenv("DEFAULT_LAT", 47.4979))
    default_lon: float = float(os.getenv("DEFAULT_LON", 19.0402))
    scheduler_enabled: bool = os.getenv("SCHEDULER_ENABLED", "true").lower() == "true"
    scheduler_interval_min: int = int(os.getenv("SCHEDULER_INTERVAL_MIN", 60))
    email_user: str = os.getenv("EMAIL_USER")
    email_pass: str = os.getenv("EMAIL_PASS")
    email_to: str = os.getenv("EMAIL_TO")


settings = Settings()
