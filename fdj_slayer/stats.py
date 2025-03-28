"""
This module provides statistical analysis and visualization for lottery draws.
"""

import math
import matplotlib.pyplot as plt
from scipy import stats


class StatsAnalysis:
    """Handles statistical analysis of lottery draws"""

    def __init__(self, max_number, max_star, number_of_numbers, number_of_stars):
        self.max_number = max_number
        self.max_star = max_star
        self.number_of_numbers = number_of_numbers
        self.number_of_stars = number_of_stars

    def analyze_randomness(self, draws):
        """
        Analyzes the randomness of generated draws using statistical tests.
        Args:
            draws: List of draw dictionaries
        Returns:
            Dictionary with analysis results
        Raises:
            ValueError: If the draws list is empty
        """
        if not draws:
            raise ValueError("Cannot analyze randomness with empty draws list")

        all_numbers, all_stars = self._extract_numbers_and_stars(draws)
        results = {"sample_size": len(draws)}

        number_results = self._analyze_dataset(
            all_numbers, "number", self.max_number)
        results.update(number_results)

        star_results = self._analyze_dataset(all_stars, "star", self.max_star)
        results.update(star_results)

        return results

    def _analyze_dataset(self, values, value_type, max_value):
        """
        Analyzes a single dataset (either numbers or stars).
        Args:
            values: List of values to analyze
            value_type: String identifier ("number" or "star")
            max_value: Maximum possible value in the dataset
        Returns:
            Dictionary with analysis results for this dataset
        """
        results = {}
        counts = self._calculate_frequencies(values, max_value)
        expected_freq = len(values) / max_value
        chi2_result = self._perform_chi_square_test(
            counts, expected_freq, max_value)
        min_max = self._find_min_max_frequencies(counts)
        stats_data = self._calculate_statistics(counts, expected_freq, min_max)

        results[f"{value_type}_frequencies"] = counts
        results[f"expected_{value_type}_freq"] = expected_freq
        results[f"{value_type}_chi2"] = chi2_result["chi2"]
        results[f"p_value_{value_type}s"] = chi2_result["p_value"]
        results[f"min_{value_type}"] = min_max["min"]
        results[f"max_{value_type}"] = min_max["max"]
        results[f"{value_type}_std_dev"] = stats_data["std_dev"]
        results[f"{value_type}_variation_pct"] = stats_data["variation_pct"]
        results[f"{value_type}_assessment"] = self._assess_randomness(
            chi2_result["p_value"])

        return results

    def _extract_numbers_and_stars(self, draws):
        """Extract all numbers and stars from the draws"""
        all_numbers = []
        all_stars = []
        for draw in draws:
            all_numbers.extend(draw['numbers'])
            all_stars.extend(draw['stars'])
        return all_numbers, all_stars

    def _calculate_frequencies(self, values, max_value):
        """Count the frequency of each value"""
        counts = {}
        for n in range(1, max_value + 1):
            counts[n] = values.count(n)
        return counts

    def _perform_chi_square_test(self, counts, expected_freq, max_value):
        """Perform chi-square test on the distribution"""
        observed = list(counts.values())
        expected = [expected_freq] * max_value
        chi2, p_value = stats.chisquare(observed, expected)
        return {"chi2": chi2, "p_value": p_value}

    def _find_min_max_frequencies(self, counts):
        """Find minimum and maximum frequencies"""
        min_count = min(counts.values())
        max_count = max(counts.values())
        min_values = [n for n, count in counts.items() if count == min_count]
        max_values = [n for n, count in counts.items() if count == max_count]
        return {
            "min": (min_values, min_count),
            "max": (max_values, max_count)
        }

    def _calculate_statistics(self, counts, expected_freq, min_max):
        """Calculate standard deviation and variation percentage"""
        std_dev = math.sqrt(sum((count - expected_freq) ** 2
                                for count in counts.values()) / len(counts))
        min_count = min_max["min"][1]
        max_count = min_max["max"][1]

        if expected_freq == 0:
            variation_pct = 0
        else:
            variation_pct = (max_count - min_count) / expected_freq * 100

        return {
            "std_dev": std_dev,
            "variation_pct": variation_pct
        }

    def _assess_randomness(self, p_value):
        """Assess randomness based on p-value"""
        return "likely random" if p_value > 0.05 else "possibly biased"


class StatsVisualization:
    """Handles visualization of lottery draw statistics"""

    def __init__(self, max_number, max_star):
        self.max_number = max_number
        self.max_star = max_star

    def display_randomness_analysis(self, results):
        """Displays the results of randomness analysis in a user-friendly format"""
        print(f"\n===== RANDOMNESS ANALYSIS =====\n"
              f"{self._format_analysis_section(results, 'number')}\n"
              f"{self._format_analysis_section(results, 'star')}\n\n"
              f"For truly reliable randomness assessment, a larger sample size may be needed.")
        if results['sample_size'] < 100:
            print(
                "Sample size is relatively small, results should be interpreted with caution.")
        self._prompt_for_visualization(results)

    def _format_analysis_section(self, results, value_type):
        """
        Formats a section of the randomness analysis output
        Args:
            results: Dictionary containing analysis results
            value_type: Either "number" or "star" to specify which analysis to format
        """
        title_suffix = "NUMBERS ANALYSIS" if value_type == "number" else "STARS ANALYSIS"
        title = f"MAIN {title_suffix}" if value_type == "number" else f"STAR {title_suffix}"
        min_key = f"min_{value_type}"
        max_key = f"max_{value_type}"
        return f"\n{title}:" \
            f"\nExpected frequency per value: {results[f'expected_{value_type}_freq']:.2f}" \
            f"\nVariation between min and max: {results[f'{value_type}_variation_pct']:.2f}%" \
            f"\nLeast frequent value(s): {results[min_key][0]} (x{results[min_key][1]})" \
            f"\nMost frequent value(s): {results[max_key][0]} (x{results[max_key][1]})" \
            f"\nStandard deviation: {results[f'{value_type}_std_dev']:.2f}" \
            f"\nChi-square value: {results[f'{value_type}_chi2']:.2f}" \
            f"\nP-value: {results[f'p_value_{value_type}s']:.4f}" \
            f"\nAssessment: {results[f'{value_type}_assessment'].upper()}"

    def _prompt_for_visualization(self, results):
        """Asks the user if they want to see a visual representation of the distribution"""
        show_viz = input(
            "\nDo you want to see the distribution visualization? (y/n): ").lower().strip()
        if show_viz in ['o', 'oui', 'y', 'yes', '']:
            self._visualize_distribution(results)

    def _visualize_distribution(self, results):
        """Creates a visualization of the number and star distributions"""
        _, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        number_config = {
            "color": "blue",
            "title": "Main Numbers Distribution",
            "tick_interval": 5
        }
        star_config = {
            "color": "green",
            "title": "Star Numbers Distribution",
            "tick_interval": 1
        }
        self._plot_frequency_distribution(
            ax1, results, "number", number_config)
        self._plot_frequency_distribution(ax2, results, "star", star_config)
        plt.tight_layout()
        plt.show()

    def _plot_frequency_distribution(self, ax, results, value_type, config=None):
        """
        Plots frequency distribution on the given axes
        Args:
            ax: Matplotlib axes to plot on
            results: Analysis results dictionary
            value_type: "number" or "star"
            config: Optional dictionary with plot configuration
        """
        config = config or {}
        color = config.get("color", "blue")
        title = config.get("title", f"{value_type.capitalize()} Distribution")
        max_value = self.max_number if value_type == "number" else self.max_star
        tick_interval = config.get("tick_interval", max(1, max_value // 10))
        values = list(results[f'{value_type}_frequencies'].keys())
        frequencies = list(results[f'{value_type}_frequencies'].values())
        expected_freq = results[f'expected_{value_type}_freq']

        ax.bar(values, frequencies, color=color, alpha=0.7)
        ax.axhline(y=expected_freq, color='r',
                   linestyle='-', label='Expected frequency')
        ax.set_title(title)
        ax.set_xlabel(value_type.capitalize())
        ax.set_ylabel('Frequency')
        ax.set_xticks(range(1, max_value + 1, tick_interval))
        ax.legend()
