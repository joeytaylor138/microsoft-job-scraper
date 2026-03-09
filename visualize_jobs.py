from azure.storage.blob import BlobServiceClient
import csv
import os
from collections import Counter
from datetime import datetime

AZURE_CONNECTION_STRING = os.getenv("AZURE_CONNECTION_STRING")
JOBS_CONTAINER = "python-jobs"
WEB_CONTAINER = "$web"
CSV_FILE = "microsoft_jobs.csv"
HTML_FILE = "index.html"

def download_csv():
    print("Downloading latest jobs CSV from Azure...")
    blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
    blob_client = blob_service_client.get_blob_client(container=JOBS_CONTAINER, blob=CSV_FILE)
    with open(CSV_FILE, "wb") as f:
        f.write(blob_client.download_blob().readall())
    print("CSV downloaded.")

def generate_chart():
    print("Generating chart...")
    titles = []
    with open(CSV_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            titles.append(row["Title"])

    # Get top 10 most common job titles
    top_titles = Counter(titles).most_common(10)
    labels = [t[0] for t in top_titles]
    values = [t[1] for t in top_titles]

    # Truncate long titles for display
    labels = [l[:40] + "..." if len(l) > 40 else l for l in labels]

    updated = datetime.now().strftime("%Y-%m-%d %H:%M")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Microsoft DC Jobs Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background-color: #f4f6f9;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 40px;
        }}
        h1 {{
            color: #0078d4;
            margin-bottom: 5px;
        }}
        p {{
            color: #666;
            margin-bottom: 30px;
        }}
        .chart-container {{
            background: white;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            width: 100%;
            max-width: 900px;
        }}
    </style>
</head>
<body>
    <h1>Microsoft Washington DC Jobs</h1>
    <p>Top 10 most common job titles — Last updated: {updated}</p>
    <div class="chart-container">
        <canvas id="jobChart"></canvas>
    </div>
    <script>
        const ctx = document.getElementById('jobChart').getContext('2d');
        new Chart(ctx, {{
            type: 'bar',
            data: {{
                labels: {labels},
                datasets: [{{
                    label: 'Number of Openings',
                    data: {values},
                    backgroundColor: '#0078d4',
                    borderRadius: 6
                }}]
            }},
            options: {{
                indexAxis: 'y',
                responsive: true,
                plugins: {{
                    legend: {{ display: false }},
                    tooltip: {{ enabled: true }}
                }},
                scales: {{
                    x: {{
                        beginAtZero: true,
                        ticks: {{ stepSize: 1 }}
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>"""

    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(html)
    print("HTML chart generated.")

def upload_chart():
    print("Uploading chart to Azure static website...")
    blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
    blob_client = blob_service_client.get_blob_client(container=WEB_CONTAINER, blob=HTML_FILE)
    with open(HTML_FILE, "rb") as f:
        blob_client.upload_blob(f, overwrite=True, content_settings={"content_type": "text/html"})
    print("Chart uploaded.")

if __name__ == "__main__":
    download_csv()
    generate_chart()
    upload_chart()
    print("\nDone! View your dashboard at:")
    print("https://jtaccountstorage.z13.web.core.windows.net")
