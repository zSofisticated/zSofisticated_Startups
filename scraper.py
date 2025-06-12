import requests
from bs4 import BeautifulSoup
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import os
from datetime import datetime
import time
import random
from urllib.parse import urljoin

# Configuration
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}
SHEET_ID = os.environ.get('SHEET_ID', '1NBxLY4qD4RpBVDTjExLnkWSZ2gj0-f0uTCkOiFnglec')

# Initialize Google Sheets
def init_gsheets():
    creds_json = os.environ.get('GCP_CREDENTIALS')
    if not creds_json:
        raise ValueError("No GCP credentials found in environment variables")
    
    creds_dict = json.loads(creds_json)
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    return client.open_by_key(SHEET_ID).sheet1

# Helper function to clean text
def clean_text(text):
    return ' '.join(text.split()).strip() if text else ''

# Scrape EU-Startups Directory
def scrape_eu_startups_directory():
    print("Scraping EU-Startups Directory...")
    base_url = "https://www.eu-startups.com"
    url = f"{base_url}/directory/"
    startups = []
    
    try:
        response = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all company listings
        company_listings = soup.select('.company-listing')
        
        for company in company_listings:
            try:
                # Extract basic information
                name = clean_text(company.select_one('.company-name').text) if company.select_one('.company-name') else ''
                website = company.select_one('.company-website a')['href'] if company.select_one('.company-website a') else ''
                description = clean_text(company.select_one('.company-description').text) if company.select_one('.company-description') else ''
                country = clean_text(company.select_one('.company-country').text) if company.select_one('.company-country') else ''
                
                # Extract additional details if available
                industry = ''
                funding_stage = ''
                date_updated = datetime.now().strftime('%Y-%m-%d')
                
                # Try to find metadata elements
                metadata = company.select('.company-meta span')
                for item in metadata:
                    text = clean_text(item.text)
                    if 'Industry:' in text:
                        industry = text.replace('Industry:', '').strip()
                    elif 'Funding:' in text:
                        funding_stage = text.replace('Funding:', '').strip()
                    elif 'Updated:' in text:
                        date_updated = text.replace('Updated:', '').strip()
                
                startups.append({
                    'Name': name,
                    'Industry': industry,
                    'Country': country,
                    'Activities': description,
                    'Website URL': website,
                    'Contact Name': '',
                    'Contact Position': '',
                    'Contact Email': '',
                    'LinkedIn Url': '',
                    'Funding Stage': funding_stage or 'Unknown',
                    'Last update': date_updated,
                    'Source': 'EU-Startups Directory'
                })
                
                # Respectful delay between requests
                time.sleep(random.uniform(1, 3))
                
            except Exception as e:
                print(f"Error processing company listing: {str(e)}")
                continue
                
    except Exception as e:
        print(f"Error scraping EU-Startups Directory: {str(e)}")
    
    return startups

# Main function
def main():
    # Initialize worksheet
    worksheet = init_gsheets()
    
    # Get existing data to avoid duplicates
    existing_data = worksheet.get_all_records()
    existing_names = [row['Name'] for row in existing_data]
    
    # Scrape EU-Startups Directory
    startups = scrape_eu_startups_directory()
    
    # Prepare new rows
    new_rows = []
    for startup in startups:
        if startup['Name'] and startup['Name'] not in existing_names:
            new_rows.append([
                startup['Name'],
                startup['Industry'],
                startup['Country'],
                startup['Activities'],
                startup['Website URL'],
                startup['Contact Name'],
                startup['Contact Position'],
                startup['Contact Email'],
                startup['LinkedIn Url'],
                startup['Funding Stage'],
                startup['Last update'],
                startup['Source']
            ])
    
    # Append new rows to sheet
    if new_rows:
        worksheet.append_rows(new_rows)
        print(f"Added {len(new_rows)} new startups to the sheet")
    else:
        print("No new startups to add")

if __name__ == "__main__":
    main()
