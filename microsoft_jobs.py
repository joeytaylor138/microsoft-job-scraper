import requests
from bs4 import BeautifulSoup
import csv

# The URL of the job board
URL = "https://apply.careers.microsoft.com/careers?start=0&location=Washington%2C++DC%2C++United+States&pid=1970393556752422&sort_by=distance&filter_distance=160&filter_include_remote=1"

# The name of the output file
CSV_FILE = "microsoft_jobs.csv"

def scrape_microsoft_jobs():
    """
    Scrapes job postings from microsoft.com/careers and saves them to a CSV file.
    """
    print(f"Fetching job listings from {URL}...")
    try:
        response = requests.get(URL, timeout=10)
        # Raise an exception if the request was not successful
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error: Could not fetch the webpage. {e}")
        return

    print("Successfully fetched the page. Parsing HTML...")
   
    # Create a BeautifulSoup object to parse the HTML
    soup = BeautifulSoup(response.text, "html.parser")
   
    # Find the ordered list that contains the job listings
    job_section = soup.find("ol", class_="list-recent-jobs")
   
    if not job_section:
        print("Could not find the job listings section on the page.")
        return
       
    # Find all the individual job listings, which are <li> elements
    job_listings = job_section.find_all("li")
   
    if not job_listings:
        print("Found the job section, but no individual job listings were present.")
        return

    print(f"Found {len(job_listings)} job listings. Extracting details...")
   
    # A list to hold all the job data we extract
    jobs_data = []

    # Loop through each job listing found
    for job in job_listings:
        # Find elements by their tag and class
        title_element = job.find("h2").find("a")
        company_element = job.find("span", class_="listing-company-name")
        location_element = job.find("span", class_="listing-location")
        job_type_element = job.find("span", class_="listing-job-type")

        # Extract the text content, using .strip() to remove leading/trailing whitespace
        title = title_element.text.strip() if title_element else "N/A"
        company = company_element.text.strip() if company_element else "N/A"
        location = location_element.text.strip() if location_element else "N/A"
        job_type = job_type_element.text.strip() if job_type_element else "N/A"
       
        # The link to the full job description is in the 'href' attribute of the title's <a> tag
        link = f"https://apply.careers.microsoft.com/careers?start=0&location=Washington%2C++DC%2C++United+States&pid=1970393556752422&sort_by=distance&filter_distance=160&filter_include_remote=1{title_element['href']}" if title_element else "N/A"
       
        # Add the job details as a dictionary to our list
        jobs_data.append({
            "Title": title,
            "Company": company,
            "Location": location,
            "Job Type": job_type,
            "Link": link
        })

    # Now, write the extracted data to a CSV file
    try:
        print(f"Writing {len(jobs_data)} jobs to {CSV_FILE}...")
        with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as file:
            # Define the column headers from the keys of the first dictionary
            fieldnames = ["Title", "Company", "Location", "Job Type", "Link"]
            writer = csv.DictWriter(file, fieldnames=fieldnames)

            writer.writeheader()  # Write the header row
            writer.writerows(jobs_data) # Write all the job data
       
        print(f"Success! Your file '{CSV_FILE}' has been created.")

    except IOError as e:
        print(f"Error: Could not write to file {CSV_FILE}. {e}")


# This is the standard Python way to make a script executable
if __name__ == "__main__":
    scrape_microsoft_jobs()