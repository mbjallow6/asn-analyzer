# src/main.py 

import asyncio
import json
import click
from datetime import datetime
from typing import List, Any
from pathlib import Path
from pydantic import HttpUrl

from src.models.data_models import ASRecord
from src.scrapers.bgp_scraper import BGPHEScraper
from src.scrapers.company_scraper import CompanyWebsiteScraper

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
            
            try:
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
                
                # Convert to serializable format
                serializable_record = self._make_serializable(record.model_dump())
                results.append(serializable_record)
                
                print(f"✅ Successfully processed AS{asn}")
                
            except Exception as e:
                print(f"❌ Error processing AS{asn}: {e}")
                # Add error record for debugging
                error_record = {
                    "asn": asn,
                    "error": str(e),
                    "scraped_at": datetime.now().isoformat()
                }
                results.append(error_record)
            
            # Rate limiting
            await asyncio.sleep(2)
        
        # Save to JSON
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Saved {len(results)} records to {output_file}")
            return results
            
        except Exception as e:
            print(f"❌ Error saving to JSON: {e}")
            raise
    
    def _make_serializable(self, obj):
        """Convert Pydantic objects to JSON-serializable format"""
        if hasattr(obj, 'model_dump'):
            return self._make_serializable(obj.model_dump())
        elif isinstance(obj, dict):
            return {key: self._make_serializable(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._make_serializable(item) for item in obj]
        elif isinstance(obj, datetime):
            return obj.isoformat()
        elif hasattr(obj, '__str__') and 'pydantic' in str(type(obj)):
            return str(obj)
        else:
            return obj

@click.command()
@click.option('--asn-file', '-f', help='File containing ASN list (one per line)')
@click.option('--asn-list', '-l', help='Comma-separated ASN list')
@click.option('--output', '-o', default='data/output/asn_results.json', help='Output JSON file')
def cli(asn_file, asn_list, output):
    """ASN Analyzer CLI Tool - Robust BGP Information Scraper"""
    
    print("🚀 Starting ASN Analyzer...")
    
    if asn_file:
        try:
            with open(asn_file, 'r') as f:
                asns = [line.strip() for line in f if line.strip()]
            print(f"📂 Loaded {len(asns)} ASNs from file: {asn_file}")
        except FileNotFoundError:
            print(f"❌ File not found: {asn_file}")
            return
    elif asn_list:
        asns = [asn.strip() for asn in asn_list.split(',')]
        print(f"📝 Processing {len(asns)} ASNs from command line")
    else:
        # Default example ASNs
        asns = ["61855", "267548", "13335"]
        print("⚠️  Using default ASN list for demo")
    
    # Validate ASNs
    valid_asns = []
    for asn in asns:
        if asn.isdigit():
            valid_asns.append(asn)
        else:
            print(f"⚠️  Skipping invalid ASN: {asn}")
    
    if not valid_asns:
        print("❌ No valid ASNs found")
        return
    
    print(f"✅ Processing {len(valid_asns)} valid ASNs")
    
    analyzer = ASNAnalyzer()
    
    try:
        asyncio.run(analyzer.process_asn_list(valid_asns, output))
        print("🎉 Analysis completed successfully!")
    except KeyboardInterrupt:
        print("\n⏹️  Analysis interrupted by user")
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        raise

def main():
    """Entry point for the application"""
    cli()

if __name__ == "__main__":
    main()