#!/usr/bin/env python
"""
BSEE Duplicate Detection Script
Identifies exact and near-duplicate files in the BSEE data directory
"""

import hashlib
import pandas as pd
from pathlib import Path
import json
from typing import Dict, List, Tuple
import numpy as np
from collections import defaultdict

class DuplicateDetector:
    def __init__(self, inventory_file: str = "specs/modules/bsee/consolidation/sub-specs/inventory.json"):
        with open(inventory_file, 'r') as f:
            self.inventory = json.load(f)
        
        self.exact_duplicates = defaultdict(list)
        self.content_duplicates = defaultdict(list)
        self.similar_structure = defaultdict(list)
        
    def find_exact_duplicates(self) -> Dict[str, List[str]]:
        """Find files with identical checksums"""
        checksum_map = defaultdict(list)
        
        for file_info in self.inventory:
            checksum = file_info.get('checksum')
            if checksum and not checksum.startswith('ERROR'):
                checksum_map[checksum].append({
                    'path': file_info['path'],
                    'size_mb': file_info['size_mb']
                })
        
        # Filter to only duplicates
        self.exact_duplicates = {
            checksum: files 
            for checksum, files in checksum_map.items() 
            if len(files) > 1
        }
        
        return self.exact_duplicates
    
    def find_similar_csv_structures(self) -> Dict[str, List[str]]:
        """Find CSV files with similar column structures"""
        csv_structures = {}
        
        for file_info in self.inventory:
            if file_info['extension'] == '.csv' and 'data_info' in file_info:
                data_info = file_info['data_info']
                if 'columns' in data_info:
                    # Create a signature from columns
                    columns = sorted(data_info['columns'])
                    signature = '|'.join(columns)
                    
                    if signature not in csv_structures:
                        csv_structures[signature] = []
                    
                    csv_structures[signature].append({
                        'path': file_info['path'],
                        'row_count': data_info.get('row_count', 0),
                        'size_mb': file_info['size_mb']
                    })
        
        # Filter to only similar structures
        self.similar_structure = {
            sig: files 
            for sig, files in csv_structures.items() 
            if len(files) > 1
        }
        
        return self.similar_structure
    
    def analyze_redundancy(self) -> Dict:
        """Analyze data redundancy patterns"""
        redundancy_analysis = {
            'production_files': [],
            'well_files': [],
            'completion_files': [],
            'lease_files': [],
            'survey_files': []
        }
        
        for file_info in self.inventory:
            path = file_info['path'].lower()
            
            if 'production' in path or 'prod' in path:
                redundancy_analysis['production_files'].append({
                    'path': file_info['path'],
                    'size_mb': file_info['size_mb'],
                    'directory': file_info['directory']
                })
            elif 'well' in path:
                redundancy_analysis['well_files'].append({
                    'path': file_info['path'],
                    'size_mb': file_info['size_mb'],
                    'directory': file_info['directory']
                })
            elif 'completion' in path or 'comp' in path:
                redundancy_analysis['completion_files'].append({
                    'path': file_info['path'],
                    'size_mb': file_info['size_mb'],
                    'directory': file_info['directory']
                })
            elif 'lease' in path:
                redundancy_analysis['lease_files'].append({
                    'path': file_info['path'],
                    'size_mb': file_info['size_mb'],
                    'directory': file_info['directory']
                })
            elif 'survey' in path or 'directional' in path:
                redundancy_analysis['survey_files'].append({
                    'path': file_info['path'],
                    'size_mb': file_info['size_mb'],
                    'directory': file_info['directory']
                })
        
        return redundancy_analysis
    
    def calculate_savings(self) -> Dict:
        """Calculate potential space savings from removing duplicates"""
        total_duplicate_size = 0
        duplicate_count = 0
        
        for checksum, files in self.exact_duplicates.items():
            # Keep one, remove rest
            sizes = [f['size_mb'] for f in files]
            total_duplicate_size += sum(sizes[1:])  # Sum all but first
            duplicate_count += len(files) - 1
        
        return {
            'duplicate_count': duplicate_count,
            'total_duplicate_size_mb': round(total_duplicate_size, 2),
            'percentage_of_total': round((total_duplicate_size / 369) * 100, 1)
        }
    
    def generate_report(self, output_file: str = "specs/modules/bsee/consolidation/sub-specs/duplicate-analysis.md"):
        """Generate comprehensive duplicate analysis report"""
        self.find_exact_duplicates()
        self.find_similar_csv_structures()
        redundancy = self.analyze_redundancy()
        savings = self.calculate_savings()
        
        report_lines = [
            "# BSEE Duplicate Analysis Report",
            "",
            "## Executive Summary",
            "",
            f"- **Exact Duplicates Found**: {len(self.exact_duplicates)} sets",
            f"- **Files That Can Be Removed**: {savings['duplicate_count']}",
            f"- **Potential Space Savings**: {savings['total_duplicate_size_mb']} MB ({savings['percentage_of_total']}%)",
            f"- **CSV Files with Identical Structure**: {len(self.similar_structure)} groups",
            "",
            "## Exact Duplicates",
            "",
            "These files have identical content (same checksum):",
            ""
        ]
        
        for checksum, files in list(self.exact_duplicates.items())[:10]:
            report_lines.append(f"### Duplicate Set (Checksum: {checksum[:8]}...)")
            report_lines.append("")
            for file_info in files:
                report_lines.append(f"- `{file_info['path']}` ({file_info['size_mb']} MB)")
            report_lines.append("")
        
        if len(self.exact_duplicates) > 10:
            report_lines.append(f"*... and {len(self.exact_duplicates) - 10} more duplicate sets*")
            report_lines.append("")
        
        # Similar structures
        report_lines.extend([
            "## Files with Similar Structure",
            "",
            "These CSV files have identical column structures:",
            ""
        ])
        
        for sig, files in list(self.similar_structure.items())[:5]:
            columns = sig.split('|')[:5]  # Show first 5 columns
            report_lines.append(f"### Structure: {', '.join(columns)}...")
            report_lines.append("")
            for file_info in files[:5]:
                report_lines.append(f"- `{file_info['path']}` ({file_info.get('row_count', 'Unknown')} rows)")
            if len(files) > 5:
                report_lines.append(f"  *... and {len(files) - 5} more files*")
            report_lines.append("")
        
        # Redundancy patterns
        report_lines.extend([
            "## Data Redundancy Patterns",
            "",
            "Files grouped by data type showing potential redundancy:",
            ""
        ])
        
        for data_type, files in redundancy.items():
            if files:
                report_lines.append(f"### {data_type.replace('_', ' ').title()}: {len(files)} files")
                
                # Group by directory
                by_dir = defaultdict(list)
                for f in files:
                    by_dir[f['directory']].append(f)
                
                for dir_name, dir_files in sorted(by_dir.items()):
                    report_lines.append(f"- `{dir_name}/`: {len(dir_files)} files")
                
                report_lines.append("")
        
        # Recommendations
        report_lines.extend([
            "## Recommendations",
            "",
            "1. **Immediate Actions**:",
            f"   - Remove {savings['duplicate_count']} exact duplicate files",
            f"   - Save {savings['total_duplicate_size_mb']} MB immediately",
            "",
            "2. **Consolidation Opportunities**:",
            "   - Merge production data from multiple directories",
            "   - Consolidate well data into single authoritative source",
            "   - Combine fragmented completion data files",
            "",
            "3. **Archive Strategy**:",
            "   - Move legacy/ files to compressed archive",
            "   - Keep only latest versions in analysis_data/",
            "   - Remove extracted files that exist in zip archives",
            ""
        ])
        
        # Write report
        with open(output_file, 'w') as f:
            f.write('\n'.join(report_lines))
        
        print(f"Duplicate analysis report saved to {output_file}")
        
        # Also save detailed JSON
        detailed_results = {
            'exact_duplicates': dict(self.exact_duplicates),
            'similar_structures': dict(self.similar_structure),
            'redundancy_analysis': redundancy,
            'potential_savings': savings
        }
        
        json_file = output_file.replace('.md', '.json')
        with open(json_file, 'w') as f:
            json.dump(detailed_results, f, indent=2)
        
        return savings


if __name__ == "__main__":
    detector = DuplicateDetector()
    savings = detector.generate_report()
    
    print("\n" + "="*50)
    print("DUPLICATE ANALYSIS COMPLETE")
    print("="*50)
    print(f"Exact Duplicates: {len(detector.exact_duplicates)} sets")
    print(f"Files to Remove: {savings['duplicate_count']}")
    print(f"Space Savings: {savings['total_duplicate_size_mb']} MB ({savings['percentage_of_total']}%)")
    print("\nDetailed report saved in specs/modules/bsee/consolidation/sub-specs/")