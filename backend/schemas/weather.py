from pydantic import BaseModel
from datetime import datetime

class WeatherOut(BaseModel):
    id: int
    temperature_c: float
    windspeed_kmh: float
    latitude: float
    longitude: float
    fetched_at: datetime

    class Config:
        from_attributes = True