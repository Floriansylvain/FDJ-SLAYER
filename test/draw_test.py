"""
Unit tests for the Draw class.
"""

import unittest
from unittest.mock import patch, MagicMock
from io import StringIO
import sys
from fdj_slayer.draw import Draw
from fdj_slayer.constants import NUMBER_OF_NUMBERS, NUMBER_OF_STARS


class TestDraw(unittest.TestCase):
    """Test suite for the Draw class"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_weather = MagicMock()
        self.mock_weather.get_weather_entropy.return_value = "a" * 64
        self.draw = Draw(self.mock_weather)

    def test_get_static_entropy_pool(self):
        """Test the static entropy pool generation"""
        pool = self.draw.get_static_entropy_pool()

        self.assertIsInstance(pool, list)
        self.assertIn("a" * 64, pool)
        self.assertEqual(len(pool), 9)

    def test_get_dynamic_entropy_pool(self):
        """Test that dynamic entropy pool returns different values"""
        pool1 = self.draw.get_dynamic_entropy_pool()
        pool2 = self.draw.get_dynamic_entropy_pool()

        self.assertIsInstance(pool1, list)
        self.assertIsInstance(pool2, list)
        self.assertEqual(len(pool1), len(pool2))
        self.assertNotEqual(pool1, pool2)

    def test_generate_seed(self):
        """Test that seed generation produces an integer from entropy pool"""
        base_pool = ["test1", "test2"]
        seed = self.draw.generate_seed(base_pool)

        self.assertIsInstance(seed, int)

    @patch('fdj_slayer.draw.random')
    def test_make_draw(self, mock_random):
        """Test the draw creation with specified numbers and stars"""
        mock_random.seed.return_value = None
        mock_random.sample.side_effect = [
            [10, 20, 30, 40, 50],
            [5, 10]
        ]

        draw = self.draw.make_draw(["test_entropy"])

        self.assertIn("seed", draw)
        self.assertIn("numbers", draw)
        self.assertIn("stars", draw)
        self.assertEqual(len(draw["numbers"]), NUMBER_OF_NUMBERS)
        self.assertEqual(len(draw["stars"]), NUMBER_OF_STARS)
        self.assertEqual(draw["numbers"], [10, 20, 30, 40, 50])
        self.assertEqual(draw["stars"], [5, 10])

    @patch('fdj_slayer.draw.Bar')
    def test_generate_draws(self, mock_bar):
        """Test generation of multiple draws"""
        mock_bar_instance = mock_bar.return_value

        self.draw.make_draw = MagicMock(
            side_effect=[{"numbers": [1, 2, 3, 4, 5],
                          "stars": [1, 2], "seed": i} for i in range(3)]
        )

        draws = self.draw.generate_draws(3)

        self.assertEqual(len(draws), 3)
        mock_bar_instance.next.assert_called()
        mock_bar_instance.finish.assert_called_once()

    def test_display_draw(self):
        """Test draw display formatting"""
        captured_output = StringIO()
        sys.stdout = captured_output

        try:
            draw = {"numbers": [1, 2, 3, 4, 5], "stars": [1, 2], "seed": 12345}
            self.draw.display_draw(draw, index=0, title="TEST")

            output = captured_output.getvalue()
            self.assertIn("TEST", output)
            self.assertIn("[1, 2, 3, 4, 5]", output)
            self.assertIn("[1, 2]", output)
        finally:
            sys.stdout = sys.__stdout__

    @patch('builtins.input')
    def test_display_additional_draws(self, mock_input):
        """Test the additional draws display functionality"""
        mock_input.side_effect = ['y', 'n']

        self.draw.display_draw = MagicMock()

        draws = [
            {"numbers": [1, 2, 3, 4, 5], "stars": [1, 2], "seed": 1},
            {"numbers": [6, 7, 8, 9, 10], "stars": [3, 4], "seed": 2},
            {"numbers": [11, 12, 13, 14, 15], "stars": [5, 6], "seed": 3}
        ]
        displayed_draws = {0}

        self.draw.display_additional_draws(draws, displayed_draws)

        self.assertEqual(len(displayed_draws), 2)
        self.draw.display_draw.assert_called_once()


if __name__ == '__main__':
    unittest.main()
