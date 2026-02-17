#!/usr/bin/env python3
"""
ABOUTME: Script to verify all tables are properly rendered in PDF
ABOUTME: Counts tables in markdown and checks HTML conversion
"""

import markdown
from markdown.extensions.tables import TableExtension
from pathlib import Path
import re

def count_markdown_tables(content):
    """Count tables in markdown by finding table separators"""
    lines = content.split('\n')
    table_count = 0
    
    for line in lines:
        # Table separator line has format: |---|---|---|
        if line.strip().startswith('|') and '---' in line:
            table_count += 1
    
    return table_count

def verify_tables():
    """Verify all tables convert properly"""
    
    # Read markdown
    md_file = Path(__file__).parent / "executive_summary.md"
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Count tables in markdown
    md_table_count = count_markdown_tables(md_content)
    print(f"📊 Tables found in markdown: {md_table_count}")
    
    # Convert to HTML
    md = markdown.Markdown(
        extensions=[
            TableExtension(),
            'extra',
            'fenced_code',
            'nl2br',
            'sane_lists'
        ],
        output_format='html5'
    )
    html_content = md.convert(md_content)
    
    # Count tables in HTML
    html_table_count = html_content.count('<table>')
    print(f"📊 Tables in HTML output: {html_table_count}")
    
    # Check for table rendering
    if html_table_count >= md_table_count:
        print(f"✅ SUCCESS: All tables rendered ({html_table_count}/{md_table_count})")
        return True
    else:
        print(f"⚠️  WARNING: Some tables may not have rendered properly")
        print(f"   Expected: {md_table_count}, Got: {html_table_count}")
        
        # Find lines with tables that might not be rendering
        lines = md_content.split('\n')
        for i, line in enumerate(lines):
            if line.strip().startswith('|') and '---' in line:
                print(f"   Table at line {i+1}: {lines[i-1][:50]}...")
        
        return False

if __name__ == "__main__":
    verify_tables()
