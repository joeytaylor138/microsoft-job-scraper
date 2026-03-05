# Microsoft Jobs Scraper

An automated web scraper that collects Microsoft job listings in Washington, DC and uploads them daily to Azure Blob Storage.

## What It Does

- Scrapes job listings from the Microsoft Careers website filtered by Washington, DC
- Handles dynamic JavaScript rendering using Playwright
- Paginates through all available job pages
- Saves results to a CSV file
- Uploads the CSV to Azure Blob Storage
- Runs automatically every day via GitHub Actions

## Technologies Used

- **Python** — Core scripting language
- **Playwright** — Browser automation for scraping JavaScript-rendered content
- **BeautifulSoup** — HTML parsing
- **Azure Blob Storage** — Cloud storage for the output CSV
- **GitHub Actions** — CI/CD pipeline for daily scheduled automation

## How It Works

1. A headless Chromium browser navigates to the Microsoft Careers page
2. The location filter is set to Washington, DC using the search input and autocomplete dropdown
3. All job listings are scraped across every page of results
4. Results are saved locally as `microsoft_jobs.csv`
5. The CSV is uploaded to an Azure Blob Storage container
6. This entire process runs automatically every day at 9AM UTC via GitHub Actions

## Output

The CSV file contains the following fields:

| Field | Description |
|-------|-------------|
| Title | Job title |
| Company | Microsoft |
| Location | Washington, DC |
| Job Type | N/A |
| Link | Direct link to the job posting |

## Setup

### Prerequisites

- Python 3.11+
- An Azure Storage Account with a container

### Install Dependencies

```bash
pip install playwright beautifulsoup4 azure-storage-blob
playwright install chromium
```

### Configuration

Set your Azure connection string as an environment variable:

```bash
export AZURE_CONNECTION_STRING="your_connection_string_here"
```

### Run Locally

```bash
python scrape_microsoft_jobs.py
```

## Automated Scheduling

This project uses GitHub Actions to run the scraper daily. The workflow is defined in `.github/workflows/scraper.yml` and triggers every day at 9AM UTC.

You can also trigger it manually from the **Actions** tab in GitHub by clicking **Run workflow**.

To use this in your own repository:
1. Fork or clone this repo
2. Add your Azure connection string as a GitHub secret named `AZURE_CONNECTION_STRING`
3. Push to main and the workflow will handle the rest
