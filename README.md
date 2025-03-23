# plages-qc

Python script to scrape and aggregate data about water quality of beaches in Quebec, Canada from the official government website.

This repository serves as a data source for [plagesquebec.com](https://plagesquebec.com/).

## Features

- Scrapes beach water quality data from Quebec's Environment Ministry
- Enriches data with images and external links using DuckDuckGo search
- Stores data in a JSON database using TinyDB
- Runs automatically every 3 hours via GitHub Actions
- Uses Tor proxy for web scraping to avoid rate limiting

## Requirements

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) package installer
- Tor (optional, required for external data enrichment)

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/plages-qc.git
cd plages-qc
```

2. Install dependencies using uv:

```bash
uv sync
```

## Usage

### Local Development

By default, when running locally, the script will only process the Bas-Saint-Laurent region to speed up development:

```bash
uv run main.py
```

To process all regions locally, set the `GITHUB_ACTIONS` environment variable:

```bash
GITHUB_ACTIONS=1 uv run main.py
```

### External Data Enrichment

The script uses DuckDuckGo search to find:

- Website links for each beach
- Representative images of each beach

To enable this feature, Tor must be running locally on port 9150:

```bash
# Start Tor (example for macOS/Linux)
tor --SOCKSPort 9150
```

## Data Structure

The script generates a `beaches_db.json` file with the following structure for each beach:

```json
{
  "municipalite": "City name",
  "plagename": "Beach name",
  "plandeau": "Water body name",
  "cote": "Water quality rating (A-C)",
  "dernierprelevement": "Last sample date",
  "image": "URL to beach image",
  "remotecontent": "URL to beach website",
  "regionid": "Region ID (01-17)",
  "regionname": "Region name"
}
```

## Data Source

Data is scraped from the [Programme Environnement-Plage](https://www.environnement.gouv.qc.ca/programmes/env-plage/index.asp) of Quebec's Ministry of Environment.

## Automation

A GitHub Actions workflow ([.github/workflows/scrape.yml](.github/workflows/scrape.yml)) runs the script every 3 hours and commits any changes to the repository.
