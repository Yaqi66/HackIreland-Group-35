import scipy.io.wavfile as wav
from typing import List, Dict, Any, Tuple
import webbrowser
import requests
import re
from urllib.parse import quote
from bs4 import BeautifulSoup
from .database import supabase as supabase_client, download_file, upload_file_to_bucket
from supabase import Client as SupabaseClient
from werkzeug.utils import secure_filename
from storage3.exceptions import StorageApiError

class ScraperBucket:
    """
    A class designed to cache the sites that we're scraping
    """
    
    def __init__(self, bucket_name: str, client: SupabaseClient):
        self.bucket_name = bucket_name
        self.supabase_client = client
    
    def scrape_page(self, url: str) -> BeautifulSoup:
        url_key = secure_filename(url)
        try:
            data = download_file(self.bucket_name, url_key)
        except StorageApiError as e:
            if int(e.status) != 404:
                # bubble the error
                raise e
            print(f'Could not find {url} in cache, going to download it')
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers)
            upload_file_to_bucket(response.content, self.bucket_name, url_key)
            data = response.content
        return BeautifulSoup(data, features="html.parser")

class GoodNewsNetworkScraper:
    """A class that scrapes 'https://www.goodnewsnetwork.org/'"""
    
    def __init__(self, scraper: ScraperBucket):
        self.scraper = scraper

    def get_news_articles(self) -> List[str]:
        """Get positive news stories from Good News Network"""
        
        soup = self.scraper.scrape_page("https://www.goodnewsnetwork.org/")
        headlines = [header.find('a') for header in soup.find_all(class_='entry-title')]
        articles = []
        for headline in headlines[:5]:
            article_soup = scraper_bucket.scrape_page(headline['href'])
            paragraphs = [p.text for p in article_soup.find(class_='td-post-content').find_all('p')]
            articles.append("\n\n".join(paragraphs[:5]))
        return articles
        
scraper_bucket = ScraperBucket(bucket_name="scraper-cache", client=supabase_client)
good_news_network_scraper = GoodNewsNetworkScraper(scraper=scraper_bucket)

# usage to get news articles
# 
# > good_news_network_scraper.get_news_articles()
# 
