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

# Scrape Crunchbase News
def scrape_crunchbase():
    print("Scraping Crunchbase News...")
    base_url = "https://news.crunchbase.com"
    url = f"{base_url}/startups/series-a-series-b-funding-europe-middle-east/"
    startups = []
    
    try:
        response = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for article in soup.select('article.post-block'):
            try:
                title = clean_text(article.select_one('h2 a').text)
                article_url = urljoin(base_url, article.select_one('h2 a')['href'])
                summary = clean_text(article.select_one('.post-block__content').text)
                
                # Get details from article page
                article_resp = requests.get(article_url, headers=HEADERS)
                article_soup = BeautifulSoup(article_resp.text, 'html.parser')
                
                # Extract metadata
                metadata = article_soup.select('.article__byline span')
                date = metadata[0].text if metadata else ''
                
                startups.append({
                    'Name': title,
                    'Industry': '',
                    'Country': '',
                    'Activities': summary,
                    'Website URL': '',
                    'Contact Name': '',
                    'Contact Position': '',
                    'Contact Email': '',
                    'LinkedIn Url': '',
                    'Funding Stage': 'Series A/B',
                    'Last update': date or datetime.now().strftime('%Y-%m-%d'),
                    'Source': 'Crunchbase'
                })
                time.sleep(random.uniform(1, 3))  # Rate limiting
            except Exception as e:
                print(f"Error processing Crunchbase article: {str(e)}")
                
    except Exception as e:
        print(f"Error scraping Crunchbase: {str(e)}")
    
    return startups

# Scrape SeedTable
def scrape_seedtable():
    print("Scraping SeedTable...")
    url = "https://www.seedtable.com/startups-europe"
    startups = []
    
    try:
        response = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for card in soup.select('.company-card'):
            try:
                name = clean_text(card.select_one('.company-name').text)
                website = card.select_one('a.company-website')['href'] if card.select_one('a.company-website') else ''
                description = clean_text(card.select_one('.company-description').text) if card.select_one('.company-description') else ''
                
                startups.append({
                    'Name': name,
                    'Industry': '',
                    'Country': '',
                    'Activities': description,
                    'Website URL': website,
                    'Contact Name': '',
                    'Contact Position': '',
                    'Contact Email': '',
                    'LinkedIn Url': '',
                    'Funding Stage': 'Series A/B',
                    'Last update': datetime.now().strftime('%Y-%m-%d'),
                    'Source': 'SeedTable'
                })
            except Exception as e:
                print(f"Error processing SeedTable startup: {str(e)}")
                
    except Exception as e:
        print(f"Error scraping SeedTable: {str(e)}")
    
    return startups

# Scrape EU-Startups
def scrape_eu_startups():
    print("Scraping EU-Startups...")
    base_url = "https://www.eu-startups.com"
    url = f"{base_url}/directory/"
    startups = []
    
    try:
        response = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for company in soup.select('.company-list-item'):
            try:
                name = clean_text(company.select_one('.company-name').text)
                website = company.select_one('.company-website a')['href'] if company.select_one('.company-website a') else ''
                description = clean_text(company.select_one('.company-description').text) if company.select_one('.company-description') else ''
                country = clean_text(company.select_one('.company-country').text) if company.select_one('.company-country') else ''
                
                startups.append({
                    'Name': name,
                    'Industry': '',
                    'Country': country,
                    'Activities': description,
                    'Website URL': website,
                    'Contact Name': '',
                    'Contact Position': '',
                    'Contact Email': '',
                    'LinkedIn Url': '',
                    'Funding Stage': 'Series A/B',
                    'Last update': datetime.now().strftime('%Y-%m-%d'),
                    'Source': 'EU-Startups'
                })
            except Exception as e:
                print(f"Error processing EU-Startups company: {str(e)}")
                
    except Exception as e:
        print(f"Error scraping EU-Startups: {str(e)}")
    
    return startups

# Scrape Sifted
def scrape_sifted():
    print("Scraping Sifted...")
    base_url = "https://sifted.eu"
    url = f"{base_url}/startups"
    startups = []
    
    try:
        response = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for item in soup.select('.article-list-item'):
            try:
                title = clean_text(item.select_one('h2').text)
                article_url = urljoin(base_url, item.select_one('a')['href'])
                summary = clean_text(item.select_one('p').text) if item.select_one('p') else ''
                
                startups.append({
                    'Name': title,
                    'Industry': '',
                    'Country': '',
                    'Activities': summary,
                    'Website URL': article_url,
                    'Contact Name': '',
                    'Contact Position': '',
                    'Contact Email': '',
                    'LinkedIn Url': '',
                    'Funding Stage': 'Series A/B',
                    'Last update': datetime.now().strftime('%Y-%m-%d'),
                    'Source': 'Sifted'
                })
            except Exception as e:
                print(f"Error processing Sifted article: {str(e)}")
                
    except Exception as e:
        print(f"Error scraping Sifted: {str(e)}")
    
    return startups

# Scrape TechCrunch
def scrape_techcrunch():
    print("Scraping TechCrunch...")
    base_url = "https://techcrunch.com"
    url = f"{base_url}/tag/european-startups/"
    startups = []
    
    try:
        response = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for post in soup.select('.post-block'):
            try:
                title = clean_text(post.select_one('.post-block__title').text)
                article_url = post.select_one('.post-block__title__link')['href']
                summary = clean_text(post.select_one('.post-block__content').text) if post.select_one('.post-block__content') else ''
                
                startups.append({
                    'Name': title,
                    'Industry': '',
                    'Country': '',
                    'Activities': summary,
                    'Website URL': article_url,
                    'Contact Name': '',
                    'Contact Position': '',
                    'Contact Email': '',
                    'LinkedIn Url': '',
                    'Funding Stage': 'Series A/B',
                    'Last update': datetime.now().strftime('%Y-%m-%d'),
                    'Source': 'TechCrunch'
                })
            except Exception as e:
                print(f"Error processing TechCrunch post: {str(e)}")
                
    except Exception as e:
        print(f"Error scraping TechCrunch: {str(e)}")
    
    return startups

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
    all_startups.extend(scrape_sifted())
    all_startups.extend(scrape_techcrunch())
    
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
