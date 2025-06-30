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
from src.utils.tracker import ProcessingTracker
from src.utils.csv_processor import CSVProcessor
from src.utils.validators import ASNValidator

class ASNAnalyzer:
    def __init__(self):
        self.bgp_scraper = BGPHEScraper()
        self.company_scraper = CompanyWebsiteScraper()
        self.tracker = ProcessingTracker()
        self.validator = ASNValidator()
    
    async def process_asn_list(self, asn_list: List[str], output_file: str = None, force_reprocess: bool = False):
        """Process a list of ASNs with incremental processing support"""
        # Generate unique output filename if not provided
        if output_file is None:
            output_file = self.tracker.generate_output_filename()
        
        # Ensure output directory exists
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        
        # Filter ASNs based on processing history
        if force_reprocess:
            new_asns = asn_list
            already_processed = []
            print("🔄 Force processing enabled - will reprocess all ASNs")
        else:
            new_asns, already_processed = self.tracker.filter_new_asns(asn_list)
        
        # Display processing summary
        print("\n" + "="*60)
        print("📊 PROCESSING SUMMARY")
        print("="*60)
        print(f"📋 Total ASNs requested: {len(asn_list)}")
        print(f"🆕 New ASNs to process: {len(new_asns)}")
        print(f"⏭️  Already processed: {len(already_processed)}")
        print(f"📁 Output file: {output_file}")
        print("="*60)
        
        if already_processed:
            print(f"⏭️  Skipping already processed ASNs: {already_processed[:5]}")
            if len(already_processed) > 5:
                print(f"     ... and {len(already_processed) - 5} more")
        
        if not new_asns:
            print("✅ All requested ASNs have already been processed!")
            print("💡 Use --force to reprocess all ASNs")
            return []
        
        results = []
        successful_count = 0
        failed_count = 0
        
        for i, asn in enumerate(new_asns, 1):
            print(f"\nProcessing AS{asn}... ({i}/{len(new_asns)})")
            
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
                
                # Mark as processed
                self.tracker.mark_asn_processed(asn)
                successful_count += 1
                
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
                failed_count += 1
            
            # Save progress periodically
            if i % 5 == 0:  # Save every 5 ASNs
                self.tracker.save_progress()
            
            # Rate limiting
            await asyncio.sleep(2)
        
        # Final save
        self.tracker.save_progress()
        
        # Save results to JSON
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            print("\n" + "="*60)
            print("📊 FINAL SUMMARY")
            print("="*60)
            print(f"✅ Successful: {successful_count}")
            print(f"❌ Failed: {failed_count}")
            print(f"📁 Output file: {output_file}")
            print(f"🕒 Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("="*60)
            
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
@click.option('--output', '-o', help='Output JSON file (auto-generated if not specified)')
@click.option('--csv-import', is_flag=True, help='Import ASNs from CSV file')
@click.option('--force', is_flag=True, help='Force reprocessing of all ASNs')
@click.option('--reset-tracking', is_flag=True, help='Reset ASN tracking database')
def cli(asn_file, asn_list, output, csv_import, force, reset_tracking):
    """ASN Analyzer CLI Tool - Enhanced with Incremental Processing"""
    
    print("🔍 ASN Analyzer - BGP and Company Information Tool")
    print("="*60)
    
    analyzer = ASNAnalyzer()
    
    # Handle reset tracking
    if reset_tracking:
        analyzer.tracker.reset_tracking()
        return
    
    # Handle CSV import
    if csv_import:
        csv_processor = CSVProcessor()
        imported_asns = csv_processor.process_csv_import()
        if imported_asns:
            print(f"\n✅ CSV import completed successfully!")
            asn_file = "data/input/asn_list.txt"  # Use updated input file
        else:
            print("❌ CSV import failed or cancelled")
            return
    
    # Load ASNs
    if asn_file:
        try:
            with open(asn_file, 'r', encoding='utf-8') as f:
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
    invalid_asns = []
    
    for asn in asns:
        normalized, suggestion = analyzer.validator.validate_and_suggest(asn)
        if normalized:
            valid_asns.append(normalized)
        else:
            invalid_asns.append((asn, suggestion))
    
    if invalid_asns:
        print(f"\n⚠️  Found {len(invalid_asns)} invalid ASNs:")
        for asn, suggestion in invalid_asns[:5]:  # Show first 5
            print(f"   ❌ {asn}: {suggestion}")
        if len(invalid_asns) > 5:
            print(f"   ... and {len(invalid_asns) - 5} more")
    
    if not valid_asns:
        print("❌ No valid ASNs found")
        return
    
    print(f"✅ Processing {len(valid_asns)} valid ASNs")
    
    try:
        asyncio.run(analyzer.process_asn_list(valid_asns, output, force))
        print("🎉 Analysis completed successfully!")
    except KeyboardInterrupt:
        print("\n⏹️  Analysis interrupted by user")
        print("💾 Progress has been saved - you can resume later")
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        raise

def main():
    """Entry point for the application"""
    cli()

if __name__ == "__main__":
    main()
