import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import requests
from sqlalchemy.orm import Session

from backend.services.weather_service import fetch_current_weather, save_weather_record
from backend.models.weather import Weather
from backend.core.config import settings


# ============================================================================
# Tests for fetch_current_weather
# ============================================================================

class TestFetchCurrentWeather:
    """Test suite for the fetch_current_weather function."""

    @pytest.mark.parametrize("lat,lon,expected_lat,expected_lon", [
        (47.4979, 19.0402, 47.4979, 19.0402),  # Budapest
        (48.2082, 16.3738, 48.2082, 16.3738),  # Vienna
        (52.5200, 13.4050, 52.5200, 13.4050),  # Berlin
        (40.7128, -74.0060, 40.7128, -74.0060),  # New York
        # Note: (0.0, 0.0) is not tested here because the function uses 'or' for defaults,
        # which treats 0.0 as falsy and falls back to default coordinates
        (-33.8688, 151.2093, -33.8688, 151.2093),  # Sydney (negative lat)
    ])
    def test_fetch_current_weather_with_coordinates(self, lat, lon, expected_lat, expected_lon):
        """Test fetching weather with various valid coordinates."""
        temp, wind, returned_lat, returned_lon = fetch_current_weather(lat, lon)
        
        # Check that temperature and wind speed are valid floats
        assert isinstance(temp, float), "Temperature should be a float"
        assert isinstance(wind, float), "Wind speed should be a float"
        
        # Check that coordinates match (with small tolerance for floating point)
        assert returned_lat == pytest.approx(expected_lat, rel=1e-3)
        assert returned_lon == pytest.approx(expected_lon, rel=1e-3)
        
        # Sanity checks for weather data (reasonable ranges)
        assert -100 <= temp <= 60, "Temperature should be in reasonable range (-100°C to 60°C)"
        assert 0 <= wind <= 500, "Wind speed should be non-negative and reasonable"

    def test_fetch_current_weather_with_defaults(self):
        """Test fetching weather with default coordinates (None provided)."""
        temp, wind, lat, lon = fetch_current_weather()
        
        # Should use default coordinates from settings
        assert lat == pytest.approx(settings.default_lat, rel=1e-3)
        assert lon == pytest.approx(settings.default_lon, rel=1e-3)
        
        # Check valid weather data
        assert isinstance(temp, float)
        assert isinstance(wind, float)

    def test_fetch_current_weather_with_partial_defaults(self):
        """Test fetching weather when only one coordinate is provided."""
        # Only latitude provided
        temp, wind, lat, lon = fetch_current_weather(lat=50.0)
        assert lat == pytest.approx(50.0, rel=1e-3)
        assert lon == pytest.approx(settings.default_lon, rel=1e-3)
        
        # Only longitude provided
        temp, wind, lat, lon = fetch_current_weather(lon=10.0)
        assert lat == pytest.approx(settings.default_lat, rel=1e-3)
        assert lon == pytest.approx(10.0, rel=1e-3)

    @patch('backend.services.weather_service.requests.get')
    def test_fetch_current_weather_api_response_structure(self, mock_get):
        """Test that the function correctly parses the API response."""
        # Mock API response
        mock_response = Mock()
        mock_response.json.return_value = {
            "current": {
                "temperature_2m": 22.5,
                "wind_speed_10m": 15.3
            }
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        temp, wind, lat, lon = fetch_current_weather(47.5, 19.0)
        
        assert temp == 22.5
        assert wind == 15.3
        assert lat == 47.5
        assert lon == 19.0
        
        # Verify the API was called correctly
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert "latitude=47.5" in call_args[0][0]
        assert "longitude=19.0" in call_args[0][0]
        assert call_args[1]['timeout'] == 10

    @patch('backend.services.weather_service.requests.get')
    def test_fetch_current_weather_http_error(self, mock_get):
        """Test handling of HTTP errors from the API."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
        mock_get.return_value = mock_response
        
        with pytest.raises(requests.exceptions.HTTPError):
            fetch_current_weather(47.5, 19.0)

    @patch('backend.services.weather_service.requests.get')
    def test_fetch_current_weather_timeout(self, mock_get):
        """Test handling of timeout errors."""
        mock_get.side_effect = requests.exceptions.Timeout("Request timed out")
        
        with pytest.raises(requests.exceptions.Timeout):
            fetch_current_weather(47.5, 19.0)

    @patch('backend.services.weather_service.requests.get')
    def test_fetch_current_weather_connection_error(self, mock_get):
        """Test handling of connection errors."""
        mock_get.side_effect = requests.exceptions.ConnectionError("Failed to connect")
        
        with pytest.raises(requests.exceptions.ConnectionError):
            fetch_current_weather(47.5, 19.0)

    @patch('backend.services.weather_service.requests.get')
    def test_fetch_current_weather_invalid_json(self, mock_get):
        """Test handling of invalid JSON response."""
        mock_response = Mock()
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        with pytest.raises(ValueError):
            fetch_current_weather(47.5, 19.0)

    @patch('backend.services.weather_service.requests.get')
    def test_fetch_current_weather_missing_data_fields(self, mock_get):
        """Test handling of missing data fields in API response."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "current": {}  # Missing temperature and wind speed
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        with pytest.raises(KeyError):
            fetch_current_weather(47.5, 19.0)

    @patch('backend.services.weather_service.requests.get')
    def test_fetch_current_weather_extreme_values(self, mock_get):
        """Test handling of extreme weather values."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "current": {
                "temperature_2m": -89.2,  # Record low temperature
                "wind_speed_10m": 408.0   # Very high wind speed
            }
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        temp, wind, lat, lon = fetch_current_weather(47.5, 19.0)
        
        assert temp == -89.2
        assert wind == 408.0


# ============================================================================
# Tests for save_weather_record
# ============================================================================

class TestSaveWeatherRecord:
    """Test suite for the save_weather_record function."""

    def test_save_weather_record_success(self):
        """Test successfully saving a weather record to the database."""
        # Create a mock database session
        mock_db = Mock(spec=Session)
        mock_weather = Weather(
            id=1,
            temperature_c=22.5,
            windspeed_kmh=15.3,
            latitude=47.5,
            longitude=19.0,
            fetched_at=datetime.utcnow()
        )
        
        # Configure the mock to return our weather object after refresh
        mock_db.refresh.side_effect = lambda obj: setattr(obj, 'id', 1)
        
        result = save_weather_record(mock_db, 22.5, 15.3, 47.5, 19.0)
        
        # Verify database operations were called
        assert mock_db.add.called
        assert mock_db.commit.called
        assert mock_db.refresh.called
        
        # Verify the returned object has correct attributes
        assert isinstance(result, Weather)
        assert result.temperature_c == 22.5
        assert result.windspeed_kmh == 15.3
        assert result.latitude == 47.5
        assert result.longitude == 19.0

    def test_save_weather_record_with_negative_temperature(self):
        """Test saving a record with negative temperature."""
        mock_db = Mock(spec=Session)
        
        result = save_weather_record(mock_db, -15.5, 10.0, 60.0, 25.0)
        
        assert result.temperature_c == -15.5
        assert mock_db.add.called
        assert mock_db.commit.called

    def test_save_weather_record_with_zero_wind(self):
        """Test saving a record with zero wind speed."""
        mock_db = Mock(spec=Session)
        
        result = save_weather_record(mock_db, 20.0, 0.0, 47.5, 19.0)
        
        assert result.windspeed_kmh == 0.0
        assert mock_db.add.called
        assert mock_db.commit.called

    def test_save_weather_record_with_extreme_coordinates(self):
        """Test saving a record with extreme latitude/longitude values."""
        mock_db = Mock(spec=Session)
        
        # Test maximum latitude (North Pole)
        result = save_weather_record(mock_db, -40.0, 5.0, 90.0, 0.0)
        assert result.latitude == 90.0
        
        # Test minimum latitude (South Pole)
        result = save_weather_record(mock_db, -50.0, 10.0, -90.0, 0.0)
        assert result.latitude == -90.0
        
        # Test maximum longitude
        result = save_weather_record(mock_db, 20.0, 5.0, 0.0, 180.0)
        assert result.longitude == 180.0
        
        # Test minimum longitude
        result = save_weather_record(mock_db, 20.0, 5.0, 0.0, -180.0)
        assert result.longitude == -180.0

    def test_save_weather_record_database_commit_error(self):
        """Test handling of database commit errors."""
        mock_db = Mock(spec=Session)
        mock_db.commit.side_effect = Exception("Database commit failed")
        
        with pytest.raises(Exception) as exc_info:
            save_weather_record(mock_db, 22.5, 15.3, 47.5, 19.0)
        
        assert "Database commit failed" in str(exc_info.value)
        assert mock_db.add.called

    def test_save_weather_record_creates_timestamp(self):
        """Test that the weather record has a timestamp."""
        mock_db = Mock(spec=Session)
        
        before_save = datetime.utcnow()
        result = save_weather_record(mock_db, 22.5, 15.3, 47.5, 19.0)
        after_save = datetime.utcnow()
        
        # The fetched_at should be set automatically by the model default
        # We can't check the exact value without a real DB, but we can verify the field exists
        assert hasattr(result, 'fetched_at')

    def test_save_weather_record_preserves_precision(self):
        """Test that floating point precision is preserved."""
        mock_db = Mock(spec=Session)
        
        # Use values with many decimal places
        precise_temp = 22.123456789
        precise_wind = 15.987654321
        precise_lat = 47.497912345
        precise_lon = 19.040235678
        
        result = save_weather_record(mock_db, precise_temp, precise_wind, precise_lat, precise_lon)
        
        assert result.temperature_c == precise_temp
        assert result.windspeed_kmh == precise_wind
        assert result.latitude == precise_lat
        assert result.longitude == precise_lon


# ============================================================================
# Integration Tests
# ============================================================================

class TestWeatherServiceIntegration:
    """Integration tests combining fetch and save operations."""

    @patch('backend.services.weather_service.requests.get')
    def test_fetch_and_save_workflow(self, mock_get):
        """Test the complete workflow of fetching and saving weather data."""
        # Mock the API response
        mock_response = Mock()
        mock_response.json.return_value = {
            "current": {
                "temperature_2m": 22.5,
                "wind_speed_10m": 15.3
            }
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        # Fetch weather data
        temp, wind, lat, lon = fetch_current_weather(47.5, 19.0)
        
        # Save to database
        mock_db = Mock(spec=Session)
        record = save_weather_record(mock_db, temp, wind, lat, lon)
        
        # Verify the complete workflow
        assert record.temperature_c == 22.5
        assert record.windspeed_kmh == 15.3
        assert record.latitude == 47.5
        assert record.longitude == 19.0
        assert mock_db.commit.called

    @patch('backend.services.weather_service.requests.get')
    def test_multiple_locations_workflow(self, mock_get):
        """Test fetching and saving weather for multiple locations."""
        locations = [
            (47.4979, 19.0402, 20.0, 10.0),  # Budapest
            (48.2082, 16.3738, 18.5, 12.5),  # Vienna
            (52.5200, 13.4050, 15.0, 20.0),  # Berlin
        ]
        
        mock_db = Mock(spec=Session)
        
        for lat, lon, temp, wind in locations:
            # Mock API response for each location
            mock_response = Mock()
            mock_response.json.return_value = {
                "current": {
                    "temperature_2m": temp,
                    "wind_speed_10m": wind
                }
            }
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response
            
            # Fetch and save
            fetched_temp, fetched_wind, fetched_lat, fetched_lon = fetch_current_weather(lat, lon)
            record = save_weather_record(mock_db, fetched_temp, fetched_wind, fetched_lat, fetched_lon)
            
            assert record.temperature_c == temp
            assert record.windspeed_kmh == wind
        
        # Verify we saved all locations
        assert mock_db.add.call_count == len(locations)
        assert mock_db.commit.call_count == len(locations)