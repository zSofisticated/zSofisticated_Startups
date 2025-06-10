import requests
from bs4 import BeautifulSoup
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import os
from datetime import datetime
import time
import random

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

# Scrape Crunchbase News
def scrape_crunchbase():
    print("Scraping Crunchbase News...")
    url = "https://news.crunchbase.com/startups/series-a-series-b-funding-europe-middle-east/"
    try:
        response = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        startups = []
        articles = soup.select('article.post-block')
        
        for article in articles:
            title = article.select_one('h2 a').text.strip()
            link = article.select_one('h2 a')['href']
            summary = article.select_one('.post-block__content').text.strip()
            
            # Extract more details from individual article page
            try:
                article_resp = requests.get(link, headers=HEADERS)
                article_soup = BeautifulSoup(article_resp.text, 'html.parser')
                
                # These selectors might need adjustment based on actual page structure
                industry = article_soup.select_one('.industry-tag').text if article_soup.select_one('.industry-tag') else ""
                country = article_soup.select_one('.country-tag').text if article_soup.select_one('.country-tag') else ""
                funding = article_soup.select_one('.funding-amount').text if article_soup.select_one('.funding-amount') else ""
                
                startups.append({
                    'Name': title,
                    'Industry': industry,
                    'Country': country,
                    'Activities': summary,
                    'Website URL': "",
                    'Contact Name': "",
                    'Contact Position': "",
                    'Contact Email': "",
                    'LinkedIn Url': "",
                    'Funding Stage': funding,
                    'Last update': datetime.now().strftime('%Y-%m-%d')
                })
            except Exception as e:
                print(f"Error scraping article {link}: {str(e)}")
                
        return startups
    except Exception as e:
        print(f"Error scraping Crunchbase: {str(e)}")
        return []

# Scrape SeedTable
def scrape_seedtable():
    print("Scraping SeedTable...")
    # Similar implementation for SeedTable
    # Would need to inspect their page structure
    return []

# Scrape EU-Startups
def scrape_eu_startups():
    print("Scraping EU-Startups...")
    # Similar implementation for EU-Startups
    return []

# Main function
def main():
    # Initialize worksheet
    worksheet = init_gsheets()
    
    # Get existing data to avoid duplicates
    existing_data = worksheet.get_all_records()
    existing_names = [row['Name'] for row in existing_data]
    
    # Scrape all sources
    all_startups = []
    all_startups.extend(scrape_crunchbase())
    all_startups.extend(scrape_seedtable())
    all_startups.extend(scrape_eu_startups())
    
    # Prepare new rows
    new_rows = []
    for startup in all_startups:
        if startup['Name'] not in existing_names:
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
                startup['Last update']
            ])
    
    # Append new rows to sheet
    if new_rows:
        worksheet.append_rows(new_rows)
        print(f"Added {len(new_rows)} new startups to the sheet")
    else:
        print("No new startups to add")

if __name__ == "__main__":
    main()
