import csv
import io
import os
from datetime import datetime
from azure.storage.blob import BlobServiceClient
from azure.communication.email import EmailClient

# ── Configuration ──────────────────────────────────────────────────────────────
AZURE_CONNECTION_STRING = os.environ.get("AZURE_CONNECTION_STRING")
ACS_CONNECTION_STRING   = os.environ.get("ACS_CONNECTION_STRING")   # Azure Communication Services
CONTAINER_NAME          = "python-jobs"
TODAY_BLOB              = "microsoft_jobs.csv"
PREVIOUS_BLOB           = "microsoft_jobs_previous.csv"
SENDER_EMAIL            = "donotreply@YOUR_DOMAIN.azurecomm.net"     # Replace with your ACS sender email
RECIPIENT_EMAIL         = "you@example.com"                          # Replace with your email
# ──────────────────────────────────────────────────────────────────────────────


def download_csv_from_blob(blob_service_client, blob_name):
    """Download a CSV blob and return a list of dicts. Returns [] if blob doesn't exist."""
    try:
        blob_client = blob_service_client.get_blob_client(container=CONTAINER_NAME, blob=blob_name)
        data = blob_client.download_blob().readall().decode("utf-8")
        reader = csv.DictReader(io.StringIO(data))
        return list(reader)
    except Exception as e:
        print(f"Could not download '{blob_name}': {e}")
        return []


def upload_blob(blob_service_client, blob_name, content: str):
    """Upload a string as a blob (overwrites if exists)."""
    blob_client = blob_service_client.get_blob_client(container=CONTAINER_NAME, blob=blob_name)
    blob_client.upload_blob(content.encode("utf-8"), overwrite=True)
    print(f"Uploaded '{blob_name}' to Azure Blob Storage.")


def find_new_jobs(today_jobs, previous_jobs):
    """Return jobs whose Link wasn't in yesterday's data."""
    previous_links = {job["Link"] for job in previous_jobs}
    return [job for job in today_jobs if job["Link"] not in previous_links]


def build_email_html(new_jobs):
    rows = ""
    for job in new_jobs:
        rows += f"""
        <tr>
            <td style="padding:8px; border:1px solid #ddd;">{job['Title']}</td>
            <td style="padding:8px; border:1px solid #ddd;">{job['Location']}</td>
            <td style="padding:8px; border:1px solid #ddd;">
                <a href="{job['Link']}">View Job</a>
            </td>
        </tr>"""

    return f"""
    <html>
    <body style="font-family:Arial,sans-serif; color:#333;">
        <h2>🆕 New Microsoft Jobs Detected</h2>
        <p>{len(new_jobs)} new job(s) found in Washington, DC as of {datetime.today().strftime('%B %d, %Y')}:</p>
        <table style="border-collapse:collapse; width:100%;">
            <thead>
                <tr style="background:#0078d4; color:white;">
                    <th style="padding:8px; text-align:left;">Title</th>
                    <th style="padding:8px; text-align:left;">Location</th>
                    <th style="padding:8px; text-align:left;">Link</th>
                </tr>
            </thead>
            <tbody>{rows}</tbody>
        </table>
        <br>
        <p style="color:#888; font-size:12px;">Sent by Microsoft Job Scraper Alert System</p>
    </body>
    </html>"""


def send_no_new_jobs_email():
    email_client = EmailClient.from_connection_string(ACS_CONNECTION_STRING)
    message = {
        "senderAddress": SENDER_EMAIL,
        "recipients": {
            "to": [{"address": RECIPIENT_EMAIL}]
        },
        "content": {
            "subject": "Microsoft Jobs Alert - No New Jobs Today",
            "html": f"""
            <html>
            <body style="font-family:Arial,sans-serif; color:#333;">
                <h2>No New Jobs Today</h2>
                <p>The daily scan ran successfully on {datetime.today().strftime('%B %d, %Y')} but no new Microsoft job postings were found in Washington, DC today.</p>
                <p style="color:#888; font-size:12px;">Sent by Microsoft Job Scraper Alert System</p>
            </body>
            </html>
            """,
            "plainText": f"The daily scan ran successfully on {datetime.today().strftime('%B %d, %Y')} but no new Microsoft job postings were found in Washington, DC today."
        }
    }
    poller = email_client.begin_send(message)
    result = poller.result()
    print(f"No new jobs email sent! Message ID: {result['id']}")


def send_email(new_jobs):
    email_client = EmailClient.from_connection_string(ACS_CONNECTION_STRING)

    message = {
        "senderAddress": SENDER_EMAIL,
        "recipients": {
            "to": [{"address": RECIPIENT_EMAIL}]
        },
        "content": {
            "subject": f"🆕 {len(new_jobs)} New Microsoft Job(s) in Washington, DC",
            "html": build_email_html(new_jobs),
            "plainText": "\n".join(
                [f"{j['Title']} | {j['Location']} | {j['Link']}" for j in new_jobs]
            )
        }
    }

    poller = email_client.begin_send(message)
    result = poller.result()
    print(f"Email sent! Message ID: {result['id']}")


def main():
    print("Connecting to Azure Blob Storage...")
    blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)

    # Download today's and yesterday's jobs
    today_jobs    = download_csv_from_blob(blob_service_client, TODAY_BLOB)
    previous_jobs = download_csv_from_blob(blob_service_client, PREVIOUS_BLOB)

    if not today_jobs:
        print("No jobs found in today's CSV. Exiting.")
        return

    # Find new jobs
    new_jobs = find_new_jobs(today_jobs, previous_jobs)
    print(f"New jobs found: {len(new_jobs)}")

    if new_jobs:
        send_email(new_jobs)
    else:
        send_no_new_jobs_email()

    # Rotate: save today's CSV as the new "previous" for tomorrow
    fieldnames = ["Title", "Company", "Location", "Job Type", "Link"]
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(today_jobs)
    upload_blob(blob_service_client, PREVIOUS_BLOB, output.getvalue())
    print("Rotated today's jobs to 'previous' for tomorrow's comparison.")


if __name__ == "__main__":
    main()