# Microsoft DC Jobs Scraper & Alert System

A fully automated Python pipeline that scrapes Microsoft's careers page for Washington, DC job postings, visualizes the top 10 most common job titles on a live web dashboard, and sends email alerts when new jobs are detected.

---

## 🔍 What It Does

- Scrapes Microsoft's careers page daily for Washington, DC job postings using a headless browser
- Stores job data in Azure Blob Storage as a CSV file
- Compares today's jobs against yesterday's to detect new postings
- Sends an HTML email alert via Azure Communication Services when new jobs are found
- Generates a visual bar chart of the top 10 most common job titles and publishes it to a live static website hosted on Azure

---

## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| Python | Core scripting language |
| Playwright | Headless browser for dynamic job page scraping |
| BeautifulSoup | HTML parsing |
| Azure Blob Storage | Cloud storage for job data CSV files |
| Azure Communication Services (ACS) | Email alert delivery |
| Azure Static Website | Hosts the live job dashboard |
| Chart.js | Frontend bar chart visualization |
| python-dotenv | Secure local environment variable management |

---

## 🏗️ Pipeline

```
scrape_microsoft_jobs.py
        ↓
  Scrapes Microsoft careers page
  Saves jobs to microsoft_jobs.csv
  Uploads CSV to Azure Blob Storage
        ↓
job_scraper_email_alert.py
        ↓
  Downloads today's CSV from Azure Blob Storage
  Compares against previous day's CSV
  Sends email alert via ACS if new jobs found
  Rotates today's CSV to previous for next comparison
        ↓
visualize_jobs.py
        ↓
  Downloads CSV from Azure Blob Storage
  Generates top 10 job titles bar chart
  Uploads HTML dashboard to Azure Static Website
```

---

## ☁️ Why Azure?

### Azure Blob Storage vs. Local File Storage or AWS S3
Azure Blob Storage was chosen over storing files locally or using AWS S3 for several reasons. Since the scripts are designed to run in the cloud on a schedule, local file storage is not viable across runs. While AWS S3 is a strong alternative, Azure Blob Storage integrates natively with the rest of the Azure ecosystem used in this project, reducing complexity and keeping all services under one platform. It also offers a generous free tier, simple Python SDK support, and built-in static website hosting — eliminating the need for a separate hosting service like Netlify or GitHub Pages.

### Azure Communication Services (ACS) vs. Gmail SMTP or SendGrid
ACS was chosen over Gmail SMTP or SendGrid because it is a fully managed, enterprise-grade Azure-native communication service. Gmail SMTP is not suitable for automated or production systems as it requires personal account credentials and has strict sending limits. SendGrid is a solid alternative but adds a third-party dependency outside of Azure. ACS keeps the entire stack within Azure, which is more aligned with real-world cloud administration workflows, and demonstrates hands-on experience with Azure services — a valuable skill for cloud and IT roles. ACS also supports custom domains, SPF/DKIM authentication, and scales easily if the project grows.

### Playwright vs. Requests + BeautifulSoup
Microsoft's careers page is dynamically rendered using JavaScript, meaning a simple HTTP request would return an empty page. Playwright launches a real headless Chromium browser that fully renders the page before scraping, making it the right tool for modern web applications. BeautifulSoup is then used to parse the rendered HTML efficiently.

---

## ⚙️ Setup

### 1. Clone the repo
```bash
git clone https://github.com/yourusername/Job_Scraper.git
cd Job_Scraper
```

### 2. Install dependencies
```bash
pip install playwright beautifulsoup4 azure-storage-blob azure-communication-email python-dotenv
playwright install chromium
```

### 3. Create a `.env` file
```
AZURE_CONNECTION_STRING=your_azure_storage_connection_string
ACS_CONNECTION_STRING=your_acs_connection_string
```

### 4. Update configuration
In `job_scraper_email_alert.py`, set your sender and recipient email:
```python
SENDER_EMAIL    = "DoNotReply@your-domain.azurecomm.net"
RECIPIENT_EMAIL = "you@outlook.com"
```

### 5. Run the pipeline
```bash
python scrape_microsoft_jobs.py
python job_scraper_email_alert.py
python visualize_jobs.py
```

---

## 📊 Live Dashboard

View the live job dashboard at:
**https://jtaccountstorage.z13.web.core.windows.net**

---

## 📁 Project Structure

```
Job_Scraper/
├── scrape_microsoft_jobs.py       # Scrapes Microsoft careers page
├── job_scraper_email_alert.py     # Detects new jobs and sends email alerts
├── visualize_jobs.py              # Generates and publishes job chart
├── .env                           # Local secrets (not committed to GitHub)
├── .gitignore                     # Excludes secrets and generated files
└── README.md                      # Project documentation
```

---

## 🔐 Security

All sensitive credentials (connection strings, API keys) are stored in a `.env` file and excluded from version control via `.gitignore`. Never hardcode secrets directly in scripts before pushing to GitHub.
