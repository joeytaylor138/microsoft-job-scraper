import os
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import csv
import time
from urllib.parse import urljoin
from azure.storage.blob import BlobServiceClient

URL = "https://apply.careers.microsoft.com/careers?start=0&location=Washington%2C++DC%2C++United+States&pid=1970393556752422&sort_by=distance&filter_distance=160&filter_include_remote=1"
BASE = "https://careers.microsoft.com"
CSV_FILE = "microsoft_jobs.csv"

connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
container_name = "python-jobs"