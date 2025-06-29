# src\scrapers\__init__.py
# This file makes the scrapers directory a Python package
from src.scrapers.bgp_scraper import BGPHEScraper
from src.scrapers.company_scraper import CompanyWebsiteScraper

__all__ = ['BGPHEScraper', 'CompanyWebsiteScraper']
