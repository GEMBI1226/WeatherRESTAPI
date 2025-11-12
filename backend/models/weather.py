from sqlalchemy import Column, Integer, Float, DateTime
from backend.core.database import Base
from datetime import datetime

class Weather(Base):
    __tablename__ = "weather"

    id = Column(Integer, primary_key=True, index=True)
    temperature_c = Column(Float, nullable=False)
    windspeed_kmh = Column(Float, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    fetched_at = Column(DateTime, default=datetime.utcnow, nullable=False)