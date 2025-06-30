# src\utils\tracker.py
"""
ASN Processing Tracker
Manages processed ASNs and generates unique output filenames
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Set, List, Dict, Any

class ProcessingTracker:
    def __init__(self, tracking_file: str = "data/input/processed_asns.json"):
        self.tracking_file = Path(tracking_file)
        self.processed_asns: Set[str] = self._load_processed_asns()
    
    def _load_processed_asns(self) -> Set[str]:
        """Load previously processed ASNs from tracking file"""
        if self.tracking_file.exists():
            try:
                with open(self.tracking_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return set(data.get('processed_asns', []))
            except (json.JSONDecodeError, IOError):
                print(f"⚠️  Warning: Could not read tracking file, starting fresh")
                return set()
        return set()
    
    def _save_processed_asns(self):
        """Save processed ASNs to tracking file"""
        # Ensure directory exists
        self.tracking_file.parent.mkdir(parents=True, exist_ok=True)
        
        tracking_data = {
            'processed_asns': list(self.processed_asns),
            'last_updated': datetime.now().isoformat(),
            'total_processed': len(self.processed_asns)
        }
        
        try:
            with open(self.tracking_file, 'w', encoding='utf-8') as f:
                json.dump(tracking_data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"⚠️  Warning: Could not save tracking file: {e}")
    
    def filter_new_asns(self, asn_list: List[str]) -> tuple[List[str], List[str]]:
        """
        Filter ASNs into new and already processed
        Returns: (new_asns, already_processed)
        """
        new_asns = [asn for asn in asn_list if asn not in self.processed_asns]
        already_processed = [asn for asn in asn_list if asn in self.processed_asns]
        return new_asns, already_processed
    
    def mark_asn_processed(self, asn: str):
        """Mark an ASN as processed"""
        self.processed_asns.add(asn)
    
    def save_progress(self):
        """Save current progress to disk"""
        self._save_processed_asns()
    
    def generate_output_filename(self, base_dir: str = "data/output") -> str:
        """Generate unique timestamped output filename"""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"asn_results_{timestamp}.json"
        return os.path.join(base_dir, filename)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get processing statistics"""
        return {
            'total_processed': len(self.processed_asns),
            'processed_asns': sorted(list(self.processed_asns)),
            'tracking_file': str(self.tracking_file)
        }
    
    def reset_tracking(self):
        """Reset all tracking data"""
        self.processed_asns.clear()
        if self.tracking_file.exists():
            self.tracking_file.unlink()
        print("🔄 Tracking data reset successfully")
