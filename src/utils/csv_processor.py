# src\utils\csv_processor.py
"""
CSV Processing Module
Handles CSV file import and ASN extraction
"""

import pandas as pd
import os
from pathlib import Path
from typing import List, Optional, Set
from .validators import ASNValidator

class CSVProcessor:
    def __init__(self):
        self.validator = ASNValidator()
    
    def prompt_for_csv_file(self) -> Optional[str]:
        """Interactive prompt for CSV file selection"""
        print("\n" + "="*50)
        print("📊 CSV IMPORT FEATURE")
        print("="*50)
        
        use_csv = input("Do you want to import ASNs from a CSV file? (y/n): ").lower().strip()
        
        if use_csv not in ['y', 'yes']:
            print("⏭️  Skipping CSV import, using existing input file")
            return None
        
        while True:
            csv_path = input("Enter the full path to your CSV file: ").strip()
            
            if not csv_path:
                print("❌ Please provide a valid file path")
                continue
            
            csv_file = Path(csv_path)
            
            if not csv_file.exists():
                print(f"❌ File not found: {csv_path}")
                retry = input("Try again? (y/n): ").lower().strip()
                if retry not in ['y', 'yes']:
                    return None
                continue
            
            if not csv_file.suffix.lower() in ['.csv', '.xlsx', '.xls']:
                print("❌ Please provide a CSV or Excel file (.csv, .xlsx, .xls)")
                continue
            
            return str(csv_file)
    
    def load_and_preview_csv(self, csv_path: str) -> Optional[pd.DataFrame]:
        """Load CSV file and show preview"""
        try:
            # Try different encodings
            encodings = ['utf-8', 'iso-8859-1', 'cp1252', 'latin1']
            df = None
            
            for encoding in encodings:
                try:
                    if csv_path.endswith('.csv'):
                        df = pd.read_csv(csv_path, encoding=encoding)
                    else:
                        df = pd.read_excel(csv_path)
                    break
                except UnicodeDecodeError:
                    continue
            
            if df is None:
                print("❌ Could not read the file with any supported encoding")
                return None
            
            print(f"\n✅ Successfully loaded CSV file: {csv_path}")
            print(f"📊 File contains {len(df)} rows and {len(df.columns)} columns")
            print("\n📋 Column names:")
            for i, col in enumerate(df.columns, 1):
                print(f"  {i}. {col}")
            
            print(f"\n🔍 First 3 rows preview:")
            print(df.head(3).to_string(index=False))
            
            return df
            
        except Exception as e:
            print(f"❌ Error loading CSV file: {e}")
            return None
    
    def prompt_for_column(self, df: pd.DataFrame) -> Optional[str]:
        """Interactive prompt for column selection"""
        while True:
            column_input = input("\nEnter the column name or number containing ASNs: ").strip()
            
            if not column_input:
                print("❌ Please provide a column name or number")
                continue
            
            # Try by number first
            if column_input.isdigit():
                col_num = int(column_input)
                if 1 <= col_num <= len(df.columns):
                    return df.columns[col_num - 1]
                else:
                    print(f"❌ Column number must be between 1 and {len(df.columns)}")
                    continue
            
            # Try by name
            if column_input in df.columns:
                return column_input
            
            # Fuzzy matching
            similar_cols = [col for col in df.columns if column_input.lower() in col.lower()]
            if similar_cols:
                print(f"❓ Did you mean one of these columns?")
                for i, col in enumerate(similar_cols, 1):
                    print(f"  {i}. {col}")
                continue
            
            print(f"❌ Column '{column_input}' not found")
    
    def extract_asns_from_column(self, df: pd.DataFrame, column_name: str) -> List[str]:
        """Extract and validate ASNs from specified column"""
        print(f"\n🔍 Extracting ASNs from column: {column_name}")
        
        # Get the column data
        column_data = df[column_name].dropna()
        
        print(f"📊 Found {len(column_data)} non-empty values in column")
        
        # Extract ASNs
        extracted_asns = []
        invalid_count = 0
        
        for value in column_data:
            # Convert to string and clean
            asn_str = str(value).strip()
            
            # Validate and normalize ASN
            normalized_asn = self.validator.normalize_asn(asn_str)
            if normalized_asn and self.validator.is_valid_asn(normalized_asn):
                extracted_asns.append(normalized_asn)
            else:
                invalid_count += 1
        
        # Remove duplicates while preserving order
        unique_asns = list(dict.fromkeys(extracted_asns))
        
        print(f"✅ Extracted {len(unique_asns)} unique valid ASNs")
        if invalid_count > 0:
            print(f"⚠️  Skipped {invalid_count} invalid entries")
        
        # Show sample of extracted ASNs
        if unique_asns:
            print(f"\n📋 Sample ASNs extracted: {unique_asns[:5]}")
            if len(unique_asns) > 5:
                print(f"   ... and {len(unique_asns) - 5} more")
        
        return unique_asns
    
    def merge_with_existing_input(self, csv_asns: List[str], input_file: str = "data/input/asn_list.txt") -> List[str]:
        """Merge CSV ASNs with existing input file"""
        existing_asns = []
        
        # Read existing ASNs if file exists
        input_path = Path(input_file)
        if input_path.exists():
            try:
                with open(input_path, 'r', encoding='utf-8') as f:
                    existing_asns = [line.strip() for line in f if line.strip()]
                print(f"📂 Loaded {len(existing_asns)} ASNs from existing input file")
            except IOError as e:
                print(f"⚠️  Warning: Could not read existing input file: {e}")
        
        # Combine and deduplicate
        all_asns = existing_asns + csv_asns
        unique_asns = list(dict.fromkeys(all_asns))  # Preserve order
        
        # Update the input file
        try:
            input_path.parent.mkdir(parents=True, exist_ok=True)
            with open(input_path, 'w', encoding='utf-8') as f:
                for asn in unique_asns:
                    f.write(f"{asn}\n")
            
            print(f"✅ Updated input file with {len(unique_asns)} total unique ASNs")
            print(f"   - Previous: {len(existing_asns)} ASNs")
            print(f"   - From CSV: {len(csv_asns)} ASNs")
            print(f"   - Total: {len(unique_asns)} ASNs")
            
        except IOError as e:
            print(f"❌ Error updating input file: {e}")
            return existing_asns  # Return original list if update fails
        
        return unique_asns
    
    def process_csv_import(self) -> Optional[List[str]]:
        """Complete CSV import workflow"""
        # Step 1: Prompt for CSV file
        csv_path = self.prompt_for_csv_file()
        if not csv_path:
            return None
        
        # Step 2: Load and preview CSV
        df = self.load_and_preview_csv(csv_path)
        if df is None:
            return None
        
        # Step 3: Select column
        column_name = self.prompt_for_column(df)
        if not column_name:
            return None
        
        # Step 4: Extract ASNs
        csv_asns = self.extract_asns_from_column(df, column_name)
        if not csv_asns:
            print("❌ No valid ASNs found in the selected column")
            return None
        
        # Step 5: Merge with existing input
        final_asns = self.merge_with_existing_input(csv_asns)
        
        return final_asns
