"""
This script generates random draws for EuroMillions using various entropy sources.
"""

import random
import numpy as _

from fdj_slayer.draw import Draw
from fdj_slayer.weather import Weather
from fdj_slayer.constants import NUMBER_OF_DRAWS


def main():
    """Main function that orchestrates the draw generation process"""
    weather = Weather()
    draw_generator = Draw(weather)

    print(f"Generating {NUMBER_OF_DRAWS} different draws...")
    draws = draw_generator.generate_draws(NUMBER_OF_DRAWS)

    base_pool = draw_generator.get_static_entropy_pool()
    random.seed(draw_generator.generate_seed(base_pool))
    chosen_draw = random.choice(draws)
    displayed_draws = {draws.index(chosen_draw)}

    draw_generator.display_draw(chosen_draw, title="FINAL RESULT")
    print("Draw selected from among the", NUMBER_OF_DRAWS, "generated")
    draw_generator.display_additional_draws(draws, displayed_draws)


if __name__ == "__main__":
    main()
