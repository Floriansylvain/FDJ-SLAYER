#!/usr/bin/env python3
"""
Simple script to generate and display a single EuroMillions draw result.
This is a non-interactive version for automated draw generation.
"""

from fdj_slayer.draw import Draw
from fdj_slayer.weather import Weather
from fdj_slayer.constants import MAX_NUMBER, MAX_STAR, NUMBER_OF_NUMBERS, NUMBER_OF_STARS


def generate_single_draw():
    """Generate and display a single draw without interactive prompts"""
    print("\n" + "="*60)
    print("FDJ SLAYER - EuroMillions Draw Generator")
    print("="*60)
    
    weather = Weather()
    draw_generator = Draw(weather)
    
    print("\nGenerating a random EuroMillions draw...")
    print("Using enhanced entropy sources for maximum randomness...\n")
    
    # Generate a single draw
    draws = draw_generator.generate_draws(1)
    
    if draws:
        result = draws[0]
        print("="*60)
        print("YOUR EUROMILLIONS DRAW RESULT")
        print("="*60)
        print(f"\n🎱 Numbers: {result['numbers']}")
        print(f"⭐ Stars:   {result['stars']}")
        print(f"\n📊 Seed used: {result['seed']}")
        print("\n" + "="*60)
        print("Good luck with your draw!")
        print("="*60)
        return result
    else:
        print("Error: Could not generate draw")
        return None


if __name__ == "__main__":
    generate_single_draw()
