# \src\__init__.py
"""
ASN Analyzer Package
====================

A tool for analyzing Autonomous System Numbers (ASNs) by scraping BGP information 
from bgp.he.net and extracting company details from their websites.

Usage:
    from src import ASNAnalyzer
    from src.models import ASInfo, CompanyInfo, ASRecord
    from src.scrapers import BGPHEScraper, CompanyWebsiteScraper
"""

# Import main classes for easy access
from src.main import ASNAnalyzer
from src.models.data_models import ASInfo, CompanyInfo, ASRecord
from src.scrapers.bgp_scraper import BGPHEScraper
from src.scrapers.company_scraper import CompanyWebsiteScraper

# Package metadata
__version__ = "1.0.0"
__author__ = "Your Team"
__email__ = "bailo.jallow@yahoo.com"
__description__ = "ASN Analysis Tool for BGP and Company Information"

# Define what gets imported with "from src import *"
__all__ = [
    # Main analyzer
    'ASNAnalyzer',
    
    # Data models
    'ASInfo',
    'CompanyInfo', 
    'ASRecord',
    
    # Scrapers
    'BGPHEScraper',
    'CompanyWebsiteScraper',
    
    # Package info
    '__version__',
    '__author__',
    '__description__'
]

# Optional: Add package-level configuration
DEFAULT_CONFIG = {
    'request_timeout': 15,
    'rate_limit_delay': 2,
    'max_retries': 3,
    'output_format': 'json',
    'user_agent': 'ASNAnalyzer/1.0'
}
