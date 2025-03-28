# FDJ SLAYER

A Python application that generates random EuroMillions lottery draws using multiple entropy sources to maximize randomness.

## Description

This project aims to create truly random EuroMillions lottery draws by combining various entropy sources including hardware information, weather data, system metrics, and cryptographic functions. It generates a configurable number of draws and allows users to view them.

## Features

- Multiple entropy sources for good randomness:
  - Weather data from [OpenMeteo API](https://open-meteo.com/)
  - Hardware and system information
  - OS random data and cryptographic functions
  - CPU/memory usage and other dynamic metrics
- Fully configurable lottery draws
- Statistical analysis of generated draws:
  - Chi-square testing for randomness verification
  - Frequency distribution analysis of numbers and stars
  - Calculation of standard deviation and variation percentages
  - P-value assessment of randomness quality
- Visualization capabilities:
  - Bar charts showing number/star distributions
  - Comparison with expected frequencies
  - Interactive display of statistical results

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Floriansylvain/FDJ-SLAYER.git
cd FDJ-SLAYER
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the main script to generate lottery draws:
```bash
python main.py
```

The program will:

1. Generate the configured number of random draws
2. Display a randomly selected draw as the final result
3. Allow you to view additional draws on request

## How It Works

The application uses a combination of entropy sources to generate truly random lottery draws:

1. **Static Entropy Sources**:
   - OS random data
   - Hardware identifiers
   - System configuration
   - Weather data from geographically random locations

2. **Dynamic Entropy Sources**:
   - Current timestamp
   - CPU and memory usage
   - Process and thread information
   - Network statistics

All sources are combined, hashed, and processed to create seeds for the random number generator that selects the lottery numbers.

## Testing

Unit tests are included to verify the functionality of all major components.

### Running Tests

Run the test suite with pytest:

```bash
python -m pytest test/
```

For a coverage report:

```bash
python -m pytest --cov-report term --cov=./fdj_slayer test/
```

## Configuration

Edit the constants in ``src/constants.py`` to modify:

| Parameter              | Description                                           |
|------------------------|-------------------------------------------------------|
| `NUMBER_OF_DRAWS`      | Number of draws to generate                           |
| `NUMBER_OF_NUMBERS`    | Number of main numbers in a draw (5 for EuroMillions) |
| `MAX_NUMBER`           | Maximum main number value (50 for EuroMillions)       |
| `NUMBER_OF_STARS`      | Number of star numbers in a draw (2 for EuroMillions) |
| `MAX_STAR`             | Maximum star number value (12 for EuroMillions)       |
| Weather API parameters | Configuration for the OpenMeteo API                   |

## Dependencies

| Package                                                            | Purpose                          |
|--------------------------------------------------------------------|----------------------------------|
| [openmeteo_requests](https://pypi.org/project/openmeteo-requests/) | Weather data retrieval           |
| [progress](https://pypi.org/project/progress/)                     | Progress bar visualization       |
| [psutil](https://pypi.org/project/psutil/)                         | System metrics collection        |
| [requests-cache](https://pypi.org/project/requests-cache/)         | Caching API requests             |
| [numpy](https://pypi.org/project/numpy/)                           | `ValuesAsNumpy()` on API results |
| [retry-requests](https://pypi.org/project/retry-requests/)         | Retry failed API requests        |
| [pytest](https://pypi.org/project/pytest/)                         | Unit testing framework           |
| [pytest-cov](https://pypi.org/project/pytest-cov/)                 | Test coverage reporting          |
| [pytest-mock](https://pypi.org/project/pytest-mock/)               | Mocking for tests                |
| [matplotlib](https://pypi.org/project/matplotlib/)                 | Data visualization               |
| [scipy](https://pypi.org/project/scipy/)                           | Statistical calculations         |

## License

[FDJ-SLAYER](https://github.com/Floriansylvain/FDJ-SLAYER) © 2025 by [Florian Sylvain](https://github.com/Floriansylvain) is licensed under [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/).
