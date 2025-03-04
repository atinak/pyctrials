# Clinical Trials API Client

A Python client for interacting with the ClinicalTrials.gov API v2. This library provides an easy-to-use interface for fetching and analyzing clinical trial data.

## Installation

You can install the package via pip:

```bash
pip install pyctrials
```

## Quick Start

```python
from pyctrials import ClinicalTrialsAPI

# Initialize the client
client = ClinicalTrialsAPI()

# Fetch trials for a specific condition
trials = client.fetch_trials("Pompe Disease")

# Display results
print(f"Found {len(trials)} trials")
print(trials[['nct_id', 'brief_title', 'overall_status']].head())
```

## Features

- Easy-to-use interface for ClinicalTrials.gov API
- Automatic pagination handling
- Retry mechanism for failed requests
- Data parsing and cleanup
- DataFrame-based output for easy analysis
- Comprehensive trial information including:
  - Trial identification
  - Status information
  - Sponsor details
  - Study design
  - Location information
  - And more...

## Documentation

### ClinicalTrialsAPI

The main class for interacting with the API.

```python
client = ClinicalTrialsAPI(max_retries=5, retry_delay=5)
```

Parameters:
- `max_retries` (int): Maximum number of retry attempts for failed requests
- `retry_delay` (int): Delay between retry attempts in seconds

### Methods

#### fetch_trials()

```python
trials = client.fetch_trials(
    condition="Pompe Disease",
    status="RECRUITING",
    page_size=10
)
```

Parameters: other parameters will follow
- `condition` (str): Medical condition to search for
- `status` (str): Trial status filter (default: 'RECRUITING') (ACTIVE_NOT_RECRUITING ┃ COMPLETED ┃ ENROLLING_BY_INVITATION ┃ NOT_YET_RECRUITING ┃ RECRUITING ┃ SUSPENDED ┃ TERMINATED ┃ WITHDRAWN ┃ AVAILABLE ┃ NO_LONGER_AVAILABLE ┃ TEMPORARILY_NOT_AVAILABLE ┃ APPROVED_FOR_MARKETING ┃ WITHHELD ┃ UNKNOWN) --> visit https://clinicaltrials.gov/data-api/api#get-/studies for more info
- `page_size` (int): Number of results per page (default: 10)

Returns:
- pandas.DataFrame containing the trial data

## Examples

### Basic Usage

```python
from pyctrials import ClinicalTrialsAPI

# Initialize client
client = ClinicalTrialsAPI()

# Fetch trials
trials = client.fetch_trials("Spinal Muscular Atrophy")

# Show unique sponsors
print(trials['sponsor'].unique())

# Get trials by phase
phase_counts = trials['phase'].value_counts()
print(phase_counts)
```

### Error Handling

```python
try:
    trials = client.fetch_trials("Rare Disease")
except Exception as e:
    print(f"An error occurred: {e}")
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Thanks to ClinicalTrials.gov for providing the API
- Built with Python, pandas, and requests

## Citation

If you use this package in your research, please cite:

```bibtex
@software{pyctrials,
  author = {Anass Tinakoua},
  title = {Clinical Trials API Client},
  year = {2024},
  publisher = {GitHub},
  url = {https://github.com/atinak/pyctrials}
}
```