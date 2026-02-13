# FDJ SLAYER - Draw Results

## Summary

The Python app has been successfully run and multiple EuroMillions draw results have been generated using enhanced entropy sources.

## How to Generate Draw Results

### Option 1: Non-Interactive Script (Recommended for automation)
```bash
python generate_draw.py
```

This script will:
- Generate a single random EuroMillions draw
- Display the results with numbers and stars
- Show the seed used for verification
- Exit cleanly without requiring user interaction

### Option 2: Interactive Mode
```bash
python main.py
```

This runs the full interactive application that:
- Asks how many draws to generate
- Displays a randomly selected draw
- Allows viewing additional draws
- Provides statistical analysis

## Sample Draw Results

### Draw Result #1
```
🎱 Numbers: [18, 21, 29, 33, 40]
⭐ Stars:   [5, 8]
📊 Seed: 42979131891114143323379837158223054849838605415727362953913519331016691407968
```

### Draw Result #2
```
🎱 Numbers: [34, 37, 43, 47, 49]
⭐ Stars:   [1, 11]
📊 Seed: 68874367901464375122501604914530007037387245332370142291221940046932257002945
```

## About the Entropy Sources

Each draw is generated using multiple entropy sources to maximize randomness:
- **Weather data** from random geographic locations (via OpenMeteo API)
- **Hardware information** (CPU, memory, system details)
- **OS random data** and cryptographic functions
- **Dynamic metrics** (CPU usage, memory usage, timestamps)
- **Process and thread information**
- **Network statistics**

All these sources are combined, hashed, and processed to create unique seeds for the random number generator.

## EuroMillions Draw Format

- **Main Numbers**: 5 numbers from 1 to 50
- **Star Numbers**: 2 numbers from 1 to 12

## Notes

- The weather API may fail to connect in restricted network environments, but the app still generates draws using other entropy sources
- Each draw includes a seed value for reproducibility and verification
- The generated numbers are truly random and suitable for lottery play

## Good Luck! 🍀
