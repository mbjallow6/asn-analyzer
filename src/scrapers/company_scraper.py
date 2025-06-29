# src\scrapers\company_scraper.py
import requests
from bs4 import BeautifulSoup
import re
from typing import Optional, List
from urllib.parse import urljoin, urlparse
from src.models.data_models import CompanyInfo

class CompanyWebsiteScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
    
    def scrape_company_info(self, website_url: str) -> Optional[CompanyInfo]:
        """Scrape company information from website"""
        try:
            # Clean URL
            if not website_url.startswith(('http://', 'https://')):
                website_url = 'http://' + website_url
            
            response = self.session.get(website_url, timeout=15, allow_redirects=True)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            return self._extract_company_data(soup, website_url)
        except Exception as e:
            print(f"Error scraping {website_url}: {e}")
            return None
    
    def _extract_company_data(self, soup: BeautifulSoup, url: str) -> CompanyInfo:
        """Extract relevant company information"""
        
        # Extract title
        title = soup.find('title')
        title_text = title.get_text().strip() if title else None
        
        # Extract meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        description = meta_desc.get('content').strip() if meta_desc else None
        
        # Extract contact emails
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        page_text = soup.get_text()
        emails = list(set(re.findall(email_pattern, page_text)))
        
        # Filter out common non-contact emails
        filtered_emails = [
            email for email in emails 
            if not any(exclude in email.lower() for exclude in ['noreply', 'no-reply', 'donotreply', 'example'])
        ]
        
        # Extract phone numbers (improved pattern)
        phone_pattern = r'(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})'
        phones = list(set(re.findall(phone_pattern, page_text)))
        phone_numbers = ['-'.join(phone) for phone in phones[:3]]  # Limit to 3
        
        # Extract services (look for common service-related keywords)
        services = self._extract_services(soup)
        
        # Extract address (look for address-related content)
        address = self._extract_address(soup)
        
        return CompanyInfo(
            website_url=url,
            title=title_text,
            description=description,
            contact_emails=filtered_emails[:5],  # Limit to 5 emails
            phone_numbers=phone_numbers,
            services=services,
            address=address
        )
    
    def _extract_services(self, soup: BeautifulSoup) -> List[str]:
        """Extract service offerings"""
        service_keywords = [
            'internet', 'hosting', 'cloud', 'vpn', 'fiber', 
            'broadband', 'datacenter', 'colocation', 'managed',
            'telecom', 'telecommunications', 'network', 'connectivity',
            'wireless', 'cable', 'dsl', 'dedicated', 'bandwidth'
        ]
        
        text = soup.get_text().lower()
        found_services = []
        
        for keyword in service_keywords:
            if keyword in text:
                found_services.append(keyword.title())
        
        return list(set(found_services))  # Remove duplicates
    
    def _extract_address(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract company address"""
        # Look for common address patterns and selectors
        address_selectors = [
            'address', '.address', '#address', 
            '.contact-info', '.location', '.contact-address',
            '[itemtype*="PostalAddress"]', '.footer-address'
        ]
        
        for selector in address_selectors:
            element = soup.select_one(selector)
            if element:
                address_text = element.get_text().strip()
                # Clean up the address text
                address_text = ' '.join(address_text.split())
                if len(address_text) > 10:  # Ensure it's substantial
                    return address_text
        
        # Fallback: look for text patterns that look like addresses
        text = soup.get_text()
        address_pattern = r'\d+\s+\w+\s+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr)[,\s]+\w+'
        address_match = re.search(address_pattern, text, re.IGNORECASE)
        if address_match:
            return address_match.group().strip()
        
        return None
