# src\utils\validators.py
"""
ASN Validation Module
Handles ASN format validation and normalization
"""

import re
from typing import Optional

class ASNValidator:
    def __init__(self):
        # ASN format patterns
        self.patterns = {
            'plain': re.compile(r'^(\d+)$'),                    # 65001
            'as_prefix': re.compile(r'^AS(\d+)$', re.I),        # AS65001
            'asdot': re.compile(r'^(\d+)\.(\d+)$'),            # 1.1 (ASDOT notation)
        }
        
        # Valid ASN ranges (RFC 6996, RFC 7300)
        self.valid_ranges = [
            (1, 23455),           # Public ASNs (original)
            (23456, 23456),       # AS_TRANS (RFC 6793)
            (64496, 64511),       # Reserved for use in docs (RFC 5398)
            (64512, 65534),       # Private Use (RFC 6996)
            (65536, 4199999999),  # 4-byte ASNs (RFC 6793)
        ]
    
    def normalize_asn(self, asn_input: str) -> Optional[str]:
        """
        Normalize various ASN formats to plain number string
        Supports: 65001, AS65001, 1.1 (ASDOT)
        """
        if not asn_input or not isinstance(asn_input, str):
            return None
        
        asn_input = asn_input.strip()
        
        # Plain number
        if self.patterns['plain'].match(asn_input):
            return asn_input
        
        # AS prefix (AS65001)
        match = self.patterns['as_prefix'].match(asn_input)
        if match:
            return match.group(1)
        
        # ASDOT notation (1.1)
        match = self.patterns['asdot'].match(asn_input)
        if match:
            high = int(match.group(1))
            low = int(match.group(2))
            asn_number = (high * 65536) + low
            return str(asn_number)
        
        return None
    
    def is_valid_asn(self, asn: str) -> bool:
        """Check if ASN is in valid ranges"""
        try:
            asn_num = int(asn)
            return any(start <= asn_num <= end for start, end in self.valid_ranges)
        except (ValueError, TypeError):
            return False
    
    def validate_and_suggest(self, asn_input: str) -> tuple[Optional[str], Optional[str]]:
        """
        Validate ASN and provide suggestions if invalid
        Returns: (normalized_asn, suggestion)
        """
        normalized = self.normalize_asn(asn_input)
        
        if not normalized:
            return None, f"Invalid format. Try: 65001, AS65001, or 1.1"
        
        if not self.is_valid_asn(normalized):
            return None, f"ASN {normalized} is outside valid ranges"
        
        return normalized, None
