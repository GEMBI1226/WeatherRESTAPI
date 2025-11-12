import pytest
from backend.services.weather_service import fetch_current_weather

@pytest.mark.parametrize("lat,lon", [
    (47.4979, 19.0402),      # Budapest
    (48.2082, 16.3738),      # Vienna
    (52.5200, 13.4050),      # Berlin
])
def test_fetch_current_weather(lat, lon):
    t, w, la, lo = fetch_current_weather(lat, lon)
    assert isinstance(t, float) and isinstance(w, float)
    assert la == pytest.approx(lat, rel=1e-3)
    assert lo == pytest.approx(lon, rel=1e-3)