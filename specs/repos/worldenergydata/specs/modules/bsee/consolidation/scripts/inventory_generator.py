#!/usr/bin/env python
"""
BSEE Data Inventory Generator
Creates comprehensive inventory of all BSEE data files for consolidation analysis
"""

import os
import hashlib
import pandas as pd
from pathlib import Path
from datetime import datetime
import json
import zipfile
from typing import Dict, List, Any

class BSEEInventoryGenerator:
    def __init__(self, data_dir: str = "data/modules/bsee"):
        self.data_dir = Path(data_dir)
        self.inventory = []
        self.stats = {
            'total_files': 0,
            'total_size_mb': 0,
            'by_type': {},
            'by_directory': {},
            'duplicates_found': 0
        }
        
    def calculate_checksum(self, filepath: Path) -> str:
        """Calculate MD5 checksum for a file"""
        md5_hash = hashlib.md5()
        try:
            with open(filepath, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    md5_hash.update(chunk)
            return md5_hash.hexdigest()
        except Exception as e:
            return f"ERROR: {str(e)}"
    
    def get_csv_info(self, filepath: Path) -> Dict:
        """Extract CSV file information"""
        info = {}
        try:
            # Read first few rows to get structure
            df = pd.read_csv(filepath, nrows=5)
            info['columns'] = list(df.columns)
            info['column_count'] = len(df.columns)
            
            # Get full row count efficiently
            with open(filepath, 'r') as f:
                row_count = sum(1 for line in f) - 1  # Subtract header
            info['row_count'] = row_count
            
            # Sample data
            info['sample_data'] = df.to_dict('records')
            
        except Exception as e:
            info['error'] = str(e)
            
        return info
    
    def get_excel_info(self, filepath: Path) -> Dict:
        """Extract Excel file information"""
        info = {}
        try:
            xl_file = pd.ExcelFile(filepath)
            info['sheets'] = xl_file.sheet_names
            info['sheet_count'] = len(xl_file.sheet_names)
            
            # Get info from first sheet
            if xl_file.sheet_names:
                df = pd.read_excel(filepath, sheet_name=xl_file.sheet_names[0], nrows=5)
                info['columns'] = list(df.columns)
                info['column_count'] = len(df.columns)
                
        except Exception as e:
            info['error'] = str(e)
            
        return info
    
    def analyze_file(self, filepath: Path) -> Dict:
        """Analyze a single file and extract metadata"""
        rel_path = filepath.relative_to(self.data_dir)
        file_info = {
            'path': str(rel_path),
            'name': filepath.name,
            'directory': str(rel_path.parent),
            'extension': filepath.suffix.lower(),
            'size_bytes': filepath.stat().st_size,
            'size_mb': round(filepath.stat().st_size / (1024 * 1024), 2),
            'modified': datetime.fromtimestamp(filepath.stat().st_mtime).isoformat(),
            'checksum': self.calculate_checksum(filepath)
        }
        
        # Get type-specific information
        if file_info['extension'] == '.csv':
            file_info['data_info'] = self.get_csv_info(filepath)
        elif file_info['extension'] in ['.xlsx', '.xls']:
            file_info['data_info'] = self.get_excel_info(filepath)
        elif file_info['extension'] == '.zip':
            try:
                with zipfile.ZipFile(filepath, 'r') as z:
                    file_info['zip_contents'] = z.namelist()
            except:
                file_info['zip_contents'] = []
        
        return file_info
    
    def generate_inventory(self):
        """Generate complete inventory of all BSEE files"""
        print(f"Scanning directory: {self.data_dir}")
        
        for root, dirs, files in os.walk(self.data_dir):
            # Skip hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                if file.startswith('.'):
                    continue
                    
                filepath = Path(root) / file
                print(f"Analyzing: {filepath.relative_to(self.data_dir)}")
                
                file_info = self.analyze_file(filepath)
                self.inventory.append(file_info)
                
                # Update statistics
                self.stats['total_files'] += 1
                self.stats['total_size_mb'] += file_info['size_mb']
                
                # Count by type
                ext = file_info['extension']
                self.stats['by_type'][ext] = self.stats['by_type'].get(ext, 0) + 1
                
                # Count by directory
                dir_name = file_info['directory'].split('/')[0] if '/' in file_info['directory'] else file_info['directory']
                self.stats['by_directory'][dir_name] = self.stats['by_directory'].get(dir_name, 0) + 1
    
    def find_duplicates(self):
        """Find duplicate files based on checksum"""
        checksum_map = {}
        
        for file_info in self.inventory:
            checksum = file_info['checksum']
            if checksum and not checksum.startswith('ERROR'):
                if checksum in checksum_map:
                    checksum_map[checksum].append(file_info['path'])
                else:
                    checksum_map[checksum] = [file_info['path']]
        
        # Find duplicates
        duplicates = {k: v for k, v in checksum_map.items() if len(v) > 1}
        self.stats['duplicates_found'] = len(duplicates)
        
        return duplicates
    
    def save_inventory(self, output_dir: str = "specs/modules/bsee/consolidation/sub-specs"):
        """Save inventory to files"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save detailed inventory as JSON
        with open(output_path / "inventory.json", 'w') as f:
            json.dump(self.inventory, f, indent=2)
        
        # Save summary as markdown
        self.generate_summary_report(output_path / "data-inventory.md")
        
        # Save duplicates report
        duplicates = self.find_duplicates()
        with open(output_path / "duplicates.json", 'w') as f:
            json.dump(duplicates, f, indent=2)
        
        print(f"\nInventory saved to {output_path}")
        
    def generate_summary_report(self, output_file: Path):
        """Generate markdown summary report"""
        report_lines = [
            "# BSEE Data Inventory Report",
            "",
            f"Generated: {datetime.now().isoformat()}",
            "",
            "## Summary Statistics",
            "",
            f"- **Total Files**: {self.stats['total_files']}",
            f"- **Total Size**: {self.stats['total_size_mb']:.2f} MB",
            f"- **Duplicate Files Found**: {self.stats['duplicates_found']}",
            "",
            "## Files by Type",
            ""
        ]
        
        for ext, count in sorted(self.stats['by_type'].items()):
            report_lines.append(f"- `{ext}`: {count} files")
        
        report_lines.extend([
            "",
            "## Files by Directory",
            ""
        ])
        
        for dir_name, count in sorted(self.stats['by_directory'].items()):
            report_lines.append(f"- `{dir_name}/`: {count} files")
        
        # Add sample files
        report_lines.extend([
            "",
            "## Sample Files",
            "",
            "### CSV Files with Most Rows",
            ""
        ])
        
        csv_files = [f for f in self.inventory if f['extension'] == '.csv' and 'data_info' in f]
        csv_files_with_rows = [f for f in csv_files if 'row_count' in f.get('data_info', {})]
        csv_files_sorted = sorted(csv_files_with_rows, 
                                 key=lambda x: x['data_info'].get('row_count', 0), 
                                 reverse=True)[:10]
        
        for file_info in csv_files_sorted:
            row_count = file_info['data_info'].get('row_count', 'Unknown')
            report_lines.append(f"- `{file_info['path']}`: {row_count:,} rows")
        
        # Write report
        with open(output_file, 'w') as f:
            f.write('\n'.join(report_lines))
        
        print(f"Summary report saved to {output_file}")


if __name__ == "__main__":
    # Generate inventory
    generator = BSEEInventoryGenerator()
    generator.generate_inventory()
    generator.save_inventory()
    
    # Print summary
    print("\n" + "="*50)
    print("INVENTORY GENERATION COMPLETE")
    print("="*50)
    print(f"Total Files: {generator.stats['total_files']}")
    print(f"Total Size: {generator.stats['total_size_mb']:.2f} MB")
    print(f"Duplicates Found: {generator.stats['duplicates_found']}")
    print("\nDetailed reports saved in specs/modules/bsee/consolidation/sub-specs/")