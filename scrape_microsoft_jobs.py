from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from azure.storage.blob import BlobServiceClient
import csv
import os
URL = "https://apply.careers.microsoft.com/careers"
CSV_FILE = "microsoft_jobs.csv"
AZURE_CONNECTION_STRING = os.environ.get("AZURE_CONNECTION_STRING")
CONTAINER_NAME = "python-jobs"

LOCATION_KEYWORDS = [
    "Washington, D.C.",
    "Washington DC",
    "Washington, DC",
    "Washington,  DC,  United States",
    "United States",
]

def parse_title(text):
    for keyword in LOCATION_KEYWORDS:
        if keyword in text:
            return text.split(keyword, 1)[0].strip()
    return text.strip()

def scrape_microsoft_jobs():
    print("Launching browser...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(URL)
        page.wait_for_timeout(5000)

        html_pages = []

        try:
            page.click('#position-location-search')
            page.wait_for_timeout(1000)
            page.type('#position-location-search', 'Washington', delay=100)
            page.wait_for_timeout(2000)

            try:
                page.wait_for_selector('div[role="option"]', timeout=5000)
                suggestions = page.query_selector_all('div[role="option"]')
                for suggestion in suggestions:
                    text = suggestion.inner_text().strip()
                    print(f"Suggestion: {repr(text)}")
                    if 'Washington' in text and 'DC' in text:
                        suggestion.click()
                        page.wait_for_timeout(1000)
                        break
            except Exception as e:
                print(f"No dropdown found: {e}")

            search_buttons = page.query_selector_all('button[aria-label="Search jobs"]')
            print(f"Found {len(search_buttons)} Search jobs buttons")
            if len(search_buttons) >= 2:
                search_buttons[1].click()
            elif len(search_buttons) == 1:
                search_buttons[0].click()

            page.wait_for_load_state('networkidle')
            page.wait_for_timeout(3000)
            print("Location filter applied.")

            page_num = 1
            while True:
                print(f"Scraping page {page_num}...")
                html_pages.append(page.content())

                next_button = page.query_selector('button[aria-label="Next jobs"]')
                if next_button is None or not next_button.is_enabled():
                    print("No more pages.")
                    break

                next_button.click()
                page.wait_for_load_state('networkidle')
                page.wait_for_timeout(2000)
                page_num += 1

        except Exception as e:
            print(f"Could not apply location filter: {e}")

        if not html_pages:
            html_pages.append(page.content())

        browser.close()

    jobs_data = []

    for html in html_pages:
        soup = BeautifulSoup(html, "html.parser")
        job_links = soup.find_all("a", href=True)

        for job in job_links:
            href = job["href"]

            if "/job/" in href:
                text = job.get_text(" ", strip=True)
                title = parse_title(text)

                link = href if href.startswith("http") else f"https://careers.microsoft.com{href}"

                if not any(j["Link"] == link for j in jobs_data):
                    jobs_data.append({
                        "Title": title,
                        "Company": "Microsoft",
                        "Location": "Washington, DC",
                        "Job Type": "N/A",
                        "Link": link
                    })

    print(f"Found {len(jobs_data)} jobs across {len(html_pages)} pages")

    with open(CSV_FILE, "w", newline="", encoding="utf-8") as file:
        fieldnames = ["Title", "Company", "Location", "Job Type", "Link"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(jobs_data)

    print("CSV file created")

def upload_to_azure():
    print("Uploading to Azure...")
    blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
    blob_client = blob_service_client.get_blob_client(container=CONTAINER_NAME, blob=CSV_FILE)

    with open(CSV_FILE, "rb") as data:
        blob_client.upload_blob(data, overwrite=True)

    print(f"Uploaded {CSV_FILE} to Azure container '{CONTAINER_NAME}'")

if __name__ == "__main__":
    scrape_microsoft_jobs()
    upload_to_azure()
