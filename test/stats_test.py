"""
Unit tests for the StatsAnalysis class in fdj_slayer.stats module
"""
import unittest
from unittest.mock import patch
import math
from fdj_slayer.stats import StatsAnalysis


class TestStatsAnalysis(unittest.TestCase):
    """Tests for the StatsAnalysis class"""

    def setUp(self):
        """Set up test fixtures before each test method"""
        self.stats_analyzer = StatsAnalysis(
            max_number=50, max_star=12, number_of_numbers=5, number_of_stars=2)

        self.sample_draws = [
            {'numbers': [1, 10, 20, 30, 40], 'stars': [1, 10]},
            {'numbers': [5, 15, 25, 35, 45], 'stars': [5, 12]},
            {'numbers': [2, 12, 22, 32, 42], 'stars': [2, 11]},
            {'numbers': [3, 13, 23, 33, 43], 'stars': [3, 8]},
            {'numbers': [4, 14, 24, 34, 44], 'stars': [4, 9]}
        ]

    def test_init(self):
        """Test initialization with correct parameters"""
        self.assertEqual(self.stats_analyzer.max_number, 50)
        self.assertEqual(self.stats_analyzer.max_star, 12)
        self.assertEqual(self.stats_analyzer.number_of_numbers, 5)
        self.assertEqual(self.stats_analyzer.number_of_stars, 2)

    def test_extract_numbers_and_stars(self):
        """Test extraction of numbers and stars from draws"""
        all_numbers, all_stars = self.stats_analyzer._extract_numbers_and_stars(
            self.sample_draws)

        expected_numbers = [1, 10, 20, 30, 40, 5, 15, 25, 35, 45, 2, 12, 22, 32, 42,
                            3, 13, 23, 33, 43, 4, 14, 24, 34, 44]
        expected_stars = [1, 10, 5, 12, 2, 11, 3, 8, 4, 9]

        self.assertEqual(sorted(all_numbers), sorted(expected_numbers))
        self.assertEqual(sorted(all_stars), sorted(expected_stars))

    def test_calculate_frequencies(self):
        """Test frequency calculation"""
        values = [1, 2, 2, 3, 3, 3, 4, 4, 4, 4]
        max_value = 5

        frequencies = self.stats_analyzer._calculate_frequencies(
            values, max_value)

        self.assertEqual(frequencies, {1: 1, 2: 2, 3: 3, 4: 4, 5: 0})
        self.assertEqual(sum(frequencies.values()), len(values))

    def test_find_min_max_frequencies(self):
        """Test finding minimum and maximum frequencies"""
        counts = {1: 5, 2: 3, 3: 3, 4: 10, 5: 0}

        min_max = self.stats_analyzer._find_min_max_frequencies(counts)

        self.assertEqual(min_max["min"], ([5], 0))
        self.assertEqual(min_max["max"], ([4], 10))

        counts = {1: 5, 2: 5, 3: 0, 4: 0, 5: 10, 6: 10}
        min_max = self.stats_analyzer._find_min_max_frequencies(counts)

        self.assertEqual(sorted(min_max["min"][0]), [3, 4])
        self.assertEqual(min_max["min"][1], 0)
        self.assertEqual(sorted(min_max["max"][0]), [5, 6])
        self.assertEqual(min_max["max"][1], 10)

    def test_calculate_statistics(self):
        """Test statistics calculation"""
        counts = {1: 5, 2: 10, 3: 15}
        expected_freq = 10
        min_max = {"min": ([1], 5), "max": ([3], 15)}

        stats_data = self.stats_analyzer._calculate_statistics(
            counts, expected_freq, min_max)

        expected_std_dev = math.sqrt(
            sum((count - expected_freq)**2 for count in [5, 10, 15]) / 3)
        expected_variation_pct = (15 - 5) / expected_freq * 100

        self.assertAlmostEqual(stats_data["std_dev"], expected_std_dev)
        self.assertAlmostEqual(
            stats_data["variation_pct"], expected_variation_pct)

    def test_assess_randomness(self):
        """Test randomness assessment based on p-value"""
        self.assertEqual(
            self.stats_analyzer._assess_randomness(0.06), "likely random")
        self.assertEqual(self.stats_analyzer._assess_randomness(
            0.05), "possibly biased")
        self.assertEqual(self.stats_analyzer._assess_randomness(
            0.04), "possibly biased")
        self.assertEqual(
            self.stats_analyzer._assess_randomness(0.8), "likely random")
        self.assertEqual(self.stats_analyzer._assess_randomness(
            0.01), "possibly biased")

    @patch('scipy.stats.chisquare')
    def test_perform_chi_square_test(self, mock_chisquare):
        """Test chi-square test with mocked scipy function"""
        mock_chisquare.return_value = (1.234, 0.567)

        counts = {1: 5, 2: 7, 3: 9}
        expected_freq = 7
        max_value = 3

        result = self.stats_analyzer._perform_chi_square_test(
            counts, expected_freq, max_value)

        mock_chisquare.assert_called_once_with([5, 7, 9], [7, 7, 7])
        self.assertEqual(result, {"chi2": 1.234, "p_value": 0.567})

    def test_analyze_dataset(self):
        """Test dataset analysis with mocked internal methods"""
        values = [1, 1, 2, 2, 2, 3, 3, 4]
        value_type = "number"
        max_value = 5

        with patch.object(self.stats_analyzer, '_calculate_frequencies') as mock_calc_freq, \
                patch.object(self.stats_analyzer, '_perform_chi_square_test') as mock_chi2, \
                patch.object(self.stats_analyzer, '_find_min_max_frequencies') as mock_min_max, \
                patch.object(self.stats_analyzer, '_calculate_statistics') as mock_stats, \
                patch.object(self.stats_analyzer, '_assess_randomness') as mock_assess:

            mock_calc_freq.return_value = {1: 2, 2: 3, 3: 2, 4: 1, 5: 0}
            mock_chi2.return_value = {"chi2": 2.5, "p_value": 0.6}
            mock_min_max.return_value = {"min": ([5], 0), "max": ([2], 3)}
            mock_stats.return_value = {"std_dev": 1.2, "variation_pct": 30.0}
            mock_assess.return_value = "likely random"

            results = self.stats_analyzer._analyze_dataset(
                values, value_type, max_value)

            self.assertEqual(results["number_frequencies"], {
                             1: 2, 2: 3, 3: 2, 4: 1, 5: 0})
            self.assertEqual(
                results["expected_number_freq"], len(values) / max_value)
            self.assertEqual(results["number_chi2"], 2.5)
            self.assertEqual(results["p_value_numbers"], 0.6)
            self.assertEqual(results["min_number"], ([5], 0))
            self.assertEqual(results["max_number"], ([2], 3))
            self.assertEqual(results["number_std_dev"], 1.2)
            self.assertEqual(results["number_variation_pct"], 30.0)
            self.assertEqual(results["number_assessment"], "likely random")

    @patch.object(StatsAnalysis, '_analyze_dataset')
    @patch.object(StatsAnalysis, '_extract_numbers_and_stars')
    def test_analyze_randomness(self, mock_extract, mock_analyze):
        """Test analyze_randomness with mocked methods to verify method interactions"""
        mock_extract.return_value = ([1, 2, 3], [4, 5])
        mock_analyze.side_effect = [
            {"number_key": "number_value"},
            {"star_key": "star_value"}
        ]

        results = self.stats_analyzer.analyze_randomness(self.sample_draws)

        mock_extract.assert_called_once_with(self.sample_draws)
        self.assertEqual(mock_analyze.call_count, 2)
        mock_analyze.assert_any_call([1, 2, 3], "number", 50)
        mock_analyze.assert_any_call([4, 5], "star", 12)

        self.assertEqual(results, {
            "sample_size": len(self.sample_draws),
            "number_key": "number_value",
            "star_key": "star_value"
        })

    @patch('scipy.stats.chisquare')
    def test_analyze_randomness_integration(self, mock_chisquare):
        """Integration test for analyze_randomness with real data"""

        mock_chisquare.return_value = (2.0, 0.8)

        results = self.stats_analyzer.analyze_randomness(self.sample_draws)

        self.assertEqual(results["sample_size"], len(self.sample_draws))
        self.assertIn("number_frequencies", results)
        self.assertIn("star_frequencies", results)
        self.assertEqual(
            len(results["number_frequencies"]), self.stats_analyzer.max_number)
        self.assertEqual(
            len(results["star_frequencies"]), self.stats_analyzer.max_star)
        self.assertEqual(results["number_assessment"], "likely random")
        self.assertEqual(results["star_assessment"], "likely random")

    def test_analyze_randomness_empty_draws(self):
        """Test behavior with empty draws list"""
        with self.assertRaises(ValueError):
            self.stats_analyzer.analyze_randomness([])


if __name__ == '__main__':
    unittest.main()
