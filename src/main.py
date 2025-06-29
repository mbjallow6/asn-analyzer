import asyncio
import json
import click
from datetime import datetime
from typing import List
from pathlib import Path

from .models.data_models import ASRecord
from .scrapers.bgp_scraper import BGPHEScraper
from .scrapers.company_scraper import CompanyWebsiteScraper

class ASNAnalyzer:
    def __init__(self):
        self.bgp_scraper = BGPHEScraper()
        self.company_scraper = CompanyWebsiteScraper()
    
    async def process_asn_list(self, asn_list: List[str], output_file: str = "data/output/asn_results.json"):
        """Process a list of ASNs and save results to JSON"""
        results = []
        
        # Ensure output directory exists
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        
        for asn in asn_list:
            print(f"Processing AS{asn}...")
            
            # Scrape BGP information
            bgp_info = self.bgp_scraper.scrape_as_info(asn)
            
            # Scrape company website if available
            company_info = None
            if bgp_info.company_website:
                company_info = self.company_scraper.scrape_company_info(
                    str(bgp_info.company_website)
                )
            
            # Create record
            record = ASRecord(
                asn=asn,
                bgp_info=bgp_info,
                company_info=company_info,
                scraped_at=datetime.now()
            )
            
            results.append(record.dict())
            
            # Rate limiting
            await asyncio.sleep(2)
        
        # Save to JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, default=str, ensure_ascii=False)
        
        print(f"✅ Saved {len(results)} records to {output_file}")
        return results

@click.command()
@click.option('--asn-file', '-f', help='File containing ASN list (one per line)')
@click.option('--asn-list', '-l', help='Comma-separated ASN list')
@click.option('--output', '-o', default='data/output/asn_results.json', help='Output JSON file')
def cli(asn_file, asn_list, output):
    """ASN Analyzer CLI Tool"""
    
    if asn_file:
        with open(asn_file, 'r') as f:
            asns = [line.strip() for line in f if line.strip()]
    elif asn_list:
        asns = [asn.strip() for asn in asn_list.split(',')]
    else:
        # Default example ASNs
        asns = ["61855", "267548", "13335"]
        print("Using default ASN list for demo")
    
    analyzer = ASNAnalyzer()
    asyncio.run(analyzer.process_asn_list(asns, output))

if __name__ == "__main__":
    cli()
