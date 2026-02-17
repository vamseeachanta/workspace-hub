#!/usr/bin/env python3
"""
ABOUTME: Generate PDFs for the three financial research documents
ABOUTME: Converts FID_COST_RESEARCH.md, detailed_budget_model.md, and RESEARCH_SUMMARY.md to PDF
"""

import markdown
from markdown.extensions.tables import TableExtension
from markdown.extensions.fenced_code import FencedCodeExtension
from weasyprint import HTML, CSS
from pathlib import Path
import re

def preprocess_markdown(content):
    """
    Preprocess markdown to ensure proper rendering.
    Add blank lines before tables if needed.
    """
    lines = content.split('\n')
    processed = []
    
    for i, line in enumerate(lines):
        # Add current line
        processed.append(line)
        
        # Check if next line is a table header
        if i < len(lines) - 1:
            next_line = lines[i + 1]
            # If next line looks like table header (starts with |)
            if next_line.strip().startswith('|') and next_line.strip().endswith('|'):
                # Check if current line is not empty and not already a table line
                if line.strip() and not line.strip().startswith('|'):
                    # Add blank line before table
                    processed.append('')
    
    return '\n'.join(processed)

def generate_pdf(markdown_file, output_pdf):
    """Generate PDF from markdown file with professional formatting."""
    
    # Read markdown content
    md_file = Path(markdown_file)
    if not md_file.exists():
        print(f"❌ File not found: {markdown_file}")
        return False
    
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Preprocess markdown
    content = preprocess_markdown(content)
    
    # Convert markdown to HTML
    md = markdown.Markdown(extensions=[
        TableExtension(),
        FencedCodeExtension(),
        'extra',
        'nl2br',
        'sane_lists'
    ])
    
    html_content = md.convert(content)
    
    # Create full HTML document with styling
    html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{md_file.stem}</title>
</head>
<body>
    {html_content}
</body>
</html>
"""
    
    # CSS for professional PDF formatting
    css = CSS(string="""
        @page {{
            size: letter;
            margin: 0.75in;
            @bottom-center {{
                content: counter(page);
                font-size: 9pt;
                color: #666;
            }}
        }}
        
        body {{
            font-family: Helvetica, Arial, sans-serif;
            font-size: 10pt;
            line-height: 1.4;
            color: #333;
        }}
        
        h1 {{
            font-size: 18pt;
            color: #1a1a1a;
            margin-top: 24pt;
            margin-bottom: 12pt;
            page-break-after: avoid;
        }}
        
        h2 {{
            font-size: 14pt;
            color: #2a2a2a;
            margin-top: 18pt;
            margin-bottom: 10pt;
            page-break-after: avoid;
            border-bottom: 1px solid #ccc;
            padding-bottom: 4pt;
        }}
        
        h3 {{
            font-size: 12pt;
            color: #3a3a3a;
            margin-top: 14pt;
            margin-bottom: 8pt;
            page-break-after: avoid;
        }}
        
        h4 {{
            font-size: 11pt;
            color: #4a4a4a;
            margin-top: 12pt;
            margin-bottom: 6pt;
            page-break-after: avoid;
        }}
        
        p {{
            margin-top: 0;
            margin-bottom: 8pt;
            orphans: 3;
            widows: 3;
        }}
        
        ul, ol {{
            margin-top: 6pt;
            margin-bottom: 10pt;
            padding-left: 24pt;
        }}
        
        li {{
            margin-bottom: 4pt;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 8pt;
            margin-bottom: 12pt;
            page-break-inside: avoid;
            font-size: 8.5pt;
            line-height: 1.3;
        }}
        
        thead {{
            display: table-header-group;
        }}
        
        tr {{
            page-break-inside: avoid;
        }}
        
        th {{
            background-color: #e8e8e8;
            font-weight: bold;
            padding: 6pt 8pt;
            text-align: left;
            border: 1px solid #999;
        }}
        
        td {{
            padding: 5pt 8pt;
            border: 1px solid #ccc;
            vertical-align: top;
        }}
        
        tr:nth-child(even) td {{
            background-color: #f7f7f7;
        }}
        
        code {{
            font-family: "Courier New", Courier, monospace;
            font-size: 8pt;
            background-color: #f5f5f5;
            padding: 2pt 4pt;
            border-radius: 2pt;
        }}
        
        pre {{
            font-family: "Courier New", Courier, monospace;
            font-size: 8pt;
            line-height: 1.3;
            background-color: #f5f5f5;
            padding: 10pt;
            border: 1px solid #ddd;
            border-radius: 3pt;
            overflow-x: auto;
            page-break-inside: avoid;
            white-space: pre-wrap;
            word-wrap: break-word;
        }}
        
        pre code {{
            background-color: transparent;
            padding: 0;
        }}
        
        blockquote {{
            margin: 12pt 0;
            padding: 8pt 12pt;
            border-left: 3pt solid #ccc;
            background-color: #f9f9f9;
            font-style: italic;
        }}
        
        hr {{
            border: none;
            border-top: 1px solid #ccc;
            margin: 16pt 0;
        }}
        
        strong {{
            font-weight: bold;
        }}
        
        em {{
            font-style: italic;
        }}
        
        a {{
            color: #0066cc;
            text-decoration: none;
        }}
        
        /* Prevent awkward breaks */
        h1, h2, h3, h4, h5, h6 {{
            page-break-after: avoid;
        }}
        
        table, figure, img {{
            page-break-inside: avoid;
        }}
        
        /* Special styling for checkmarks and status indicators */
        p:contains("✅"), li:contains("✅") {{
            color: #006600;
        }}
        
        p:contains("❌"), li:contains("❌") {{
            color: #cc0000;
        }}
        
        p:contains("⚠️"), li:contains("⚠️") {{
            color: #cc6600;
        }}
    """)
    
    # Generate PDF
    HTML(string=html_template).write_pdf(output_pdf, stylesheets=[css])
    
    # Get file size
    pdf_size = Path(output_pdf).stat().st_size / 1024  # KB
    
    print(f"✅ PDF generated: {output_pdf}")
    print(f"   File size: {pdf_size:.1f} KB")
    
    return True

def main():
    """Generate PDFs for all three financial research documents."""
    
    base_path = Path(__file__).parent
    
    documents = [
        {
            'name': 'FID Cost Research',
            'markdown': base_path / 'FID_COST_RESEARCH.md',
            'pdf': base_path / 'FID_COST_RESEARCH.pdf'
        },
        {
            'name': 'Detailed Budget Model',
            'markdown': base_path / 'detailed_budget_model.md',
            'pdf': base_path / 'detailed_budget_model.pdf'
        },
        {
            'name': 'Research Summary',
            'markdown': base_path / 'RESEARCH_SUMMARY.md',
            'pdf': base_path / 'RESEARCH_SUMMARY.pdf'
        }
    ]
    
    print("=" * 70)
    print("Generating PDFs for Financial Research Documents")
    print("=" * 70)
    print()
    
    success_count = 0
    total_size = 0
    
    for doc in documents:
        print(f"Processing: {doc['name']}")
        print(f"  Source: {doc['markdown'].name}")
        
        if generate_pdf(doc['markdown'], doc['pdf']):
            success_count += 1
            pdf_size = doc['pdf'].stat().st_size / 1024
            total_size += pdf_size
        
        print()
    
    print("=" * 70)
    print(f"✅ Successfully generated {success_count}/{len(documents)} PDFs")
    print(f"📊 Total size: {total_size:.1f} KB")
    print("=" * 70)
    print()
    print("Generated PDFs:")
    for doc in documents:
        if doc['pdf'].exists():
            size = doc['pdf'].stat().st_size / 1024
            print(f"  • {doc['pdf'].name} ({size:.1f} KB)")

if __name__ == '__main__':
    main()
