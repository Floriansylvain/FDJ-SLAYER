"""
Main entry point for the FDJ Slayer application.
"""

import random
from fdj_slayer.draw import Draw
from fdj_slayer.stats import StatsAnalysis, StatsVisualization
from fdj_slayer.weather import Weather
from fdj_slayer.constants import MAX_NUMBER, MAX_STAR, NUMBER_OF_NUMBERS, NUMBER_OF_STARS


def main():
    """Main entry point for the application"""
    weather = Weather()
    stats_analyzer = StatsAnalysis(
        MAX_NUMBER, MAX_STAR, NUMBER_OF_NUMBERS, NUMBER_OF_STARS)
    stats_visualizer = StatsVisualization(MAX_NUMBER, MAX_STAR)
    draw = Draw(weather)

    print("\nWelcome to FDJ SLAYER - Your EuroMillions Number Generator!")

    try:
        num_draws = int(input("\nHow many draws would you like to generate? "))
    except ValueError:
        num_draws = 5
        print(f"Invalid input, defaulting to {num_draws} draws.")

    print("\nGenerating random draws with enhanced entropy...")
    draws = draw.generate_draws(num_draws)

    if draws:
        displayed = set()
        random_index = random.randint(0, len(draws) - 1)
        draw.display_draw(
            draws[random_index], random_index, "RANDOMLY SELECTED DRAW")
        displayed.add(random_index)

        draw.display_additional_draws(draws, displayed)

        print("\nAnalyzing randomness of the generated draws...")
        analysis = stats_analyzer.analyze_randomness(draws)
        stats_visualizer.display_randomness_analysis(analysis)


if __name__ == "__main__":
    main()
