"""
Unit tests for the Weather class.
"""

import unittest
from unittest.mock import patch
from fdj_slayer.weather import Weather


class TestWeather(unittest.TestCase):
    """Test suite for the Weather class"""

    def setUp(self):
        self.weather = Weather()

    @patch('fdj_slayer.weather.Weather._get_weather_data')
    def test_get_weather_entropy_success(self, mock_get_data):
        """Test the get_weather_entropy method"""
        expected_hash = "a" * 64
        mock_get_data.return_value = expected_hash

        result = self.weather.get_weather_entropy()
        self.assertEqual(result, expected_hash)

    @patch('fdj_slayer.weather.Weather._get_weather_data')
    def test_get_weather_entropy_fallback(self, mock_get_data):
        """Test the get_weather_entropy method when the API fails"""
        mock_get_data.side_effect = Exception("API Error")

        result = self.weather.get_weather_entropy()

        self.assertEqual(len(result), 64)
        self.assertTrue(all(c in '0123456789abcdef' for c in result))


if __name__ == '__main__':
    unittest.main()
