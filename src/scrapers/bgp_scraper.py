# src\scrapers\bgp_scraper.py
import requests
from bs4 import BeautifulSoup
import re
from typing import Optional
from src.models.data_models import ASInfo

class BGPHEScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def scrape_as_info(self, asn: str) -> ASInfo:
        """Scrape AS information from bgp.he.net"""
        url = f"https://bgp.he.net/AS{asn}#_asinfo"
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            return self._parse_as_info(soup, asn)
        except Exception as e:
            print(f"Error scraping AS{asn}: {e}")
            return ASInfo(asn=asn)
    
    def _parse_as_info(self, soup: BeautifulSoup, asn: str) -> ASInfo:
        """Parse AS information from HTML"""
        data = {"asn": asn}
        
        # Extract company website
        website_link = soup.find('a', href=re.compile(r'^http'))
        if website_link:
            data['company_website'] = website_link.get('href')
        
        # Extract country
        country_img = soup.find('img', alt=True)
        if country_img:
            data['country'] = country_img.get('alt')
        
        # Extract numerical data using regex patterns
        text_content = soup.get_text()
        
        patterns = {
            'prefixes_originated_all': r'Prefixes Originated \(all\):\s*(\d+)',
            'prefixes_originated_v4': r'Prefixes Originated \(v4\):\s*(\d+)',
            'prefixes_originated_v6': r'Prefixes Originated \(v6\):\s*(\d+)',
            'rpki_valid_all': r'RPKI Originated Valid \(all\):\s*(\d+)',
            'rpki_invalid_all': r'RPKI Originated Invalid \(all\):\s*(\d+)',
            'bgp_peers_observed_all': r'BGP Peers Observed \(all\):\s*(\d+)',
            'ips_originated_v4': r'IPs Originated \(v4\):\s*([\d,]+)',
            'avg_path_length_all': r'Average AS Path Length \(all\):\s*([\d.]+)',
        }
        
        for field, pattern in patterns.items():
            match = re.search(pattern, text_content)
            if match:
                value = match.group(1).replace(',', '')
                if field == 'avg_path_length_all':
                    data[field] = float(value)
                else:
                    data[field] = int(value)
        
        return ASInfo(**data)
