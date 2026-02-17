#!/usr/bin/env python3
"""
ABOUTME: Script to generate PDF from executive_summary.md with proper formatting
ABOUTME: Preserves ASCII diagrams, tables, and ensures professional layout
"""

import markdown
from markdown.extensions.tables import TableExtension
from markdown.extensions.fenced_code import FencedCodeExtension
from markdown.extensions.nl2br import Nl2BrExtension
from weasyprint import HTML, CSS
from pathlib import Path
import re

def preprocess_markdown(content):
    """Preprocess markdown to ensure tables render properly
    
    Markdown tables require blank lines before and after to be recognized.
    This function ensures all tables have proper spacing.
    """
    lines = content.split('\n')
    processed = []
    in_table = False
    prev_was_table = False
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Check if this is a table line (starts with | and has at least one more |)
        is_table_line = stripped.startswith('|') and stripped.count('|') >= 2
        
        # Entering a table
        if is_table_line and not in_table:
            # Ensure blank line before table
            if processed and processed[-1].strip() != '':
                processed.append('')
            in_table = True
            processed.append(line)
            prev_was_table = False
        
        # In a table
        elif is_table_line and in_table:
            processed.append(line)
            prev_was_table = True
        
        # Leaving a table
        elif not is_table_line and in_table:
            # Ensure blank line after table
            if stripped != '':
                processed.append('')
            in_table = False
            processed.append(line)
            prev_was_table = False
        
        # Not in a table
        else:
            processed.append(line)
            prev_was_table = False
    
    return '\n'.join(processed)

def generate_pdf():
    """Generate PDF from executive summary markdown"""
    
    # Read the markdown file
    md_file = Path(__file__).parent / "executive_summary.md"
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Preprocess markdown
    md_content = preprocess_markdown(md_content)
    
    # Convert markdown to HTML with proper extensions
    md = markdown.Markdown(
        extensions=[
            TableExtension(),
            FencedCodeExtension(),
            Nl2BrExtension(),
            'extra',
            'sane_lists'
        ],
        output_format='html5'
    )
    html_content = md.convert(md_content)
    
    # Create full HTML document with CSS styling
    full_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Shenandoah Field Economic Analysis - Executive Summary</title>
    <style>
        @page {{
            size: Letter;
            margin: 0.75in;
            @bottom-center {{
                content: "Page " counter(page) " of " counter(pages);
                font-size: 9pt;
                color: #666;
            }}
        }}
        
        body {{
            font-family: "Helvetica", "Arial", sans-serif;
            font-size: 10pt;
            line-height: 1.4;
            color: #333;
            max-width: 100%;
        }}
        
        h1 {{
            font-size: 18pt;
            font-weight: bold;
            color: #1a1a1a;
            border-bottom: 2px solid #333;
            padding-bottom: 8pt;
            margin-top: 20pt;
            margin-bottom: 12pt;
            page-break-after: avoid;
        }}
        
        h2 {{
            font-size: 14pt;
            font-weight: bold;
            color: #2a2a2a;
            margin-top: 16pt;
            margin-bottom: 10pt;
            page-break-after: avoid;
        }}
        
        h3 {{
            font-size: 12pt;
            font-weight: bold;
            color: #3a3a3a;
            margin-top: 12pt;
            margin-bottom: 8pt;
            page-break-after: avoid;
        }}
        
        h4 {{
            font-size: 11pt;
            font-weight: bold;
            color: #4a4a4a;
            margin-top: 10pt;
            margin-bottom: 6pt;
            page-break-after: avoid;
        }}
        
        p {{
            margin: 6pt 0;
            text-align: justify;
        }}
        
        /* Tables */
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 12pt 0;
            font-size: 8.5pt;
            page-break-inside: auto;
            border: 1px solid #999;
        }}
        
        thead {{
            display: table-header-group;
        }}
        
        tbody {{
            display: table-row-group;
        }}
        
        th {{
            background-color: #e8e8e8;
            font-weight: bold;
            padding: 7pt 5pt;
            border: 1px solid #999;
            text-align: left;
            vertical-align: top;
            page-break-after: avoid;
            page-break-inside: avoid;
        }}
        
        td {{
            padding: 6pt 5pt;
            border: 1px solid #ccc;
            vertical-align: top;
            line-height: 1.3;
        }}
        
        tr {{
            page-break-inside: avoid;
        }}
        
        tr:nth-child(even) {{
            background-color: #f7f7f7;
        }}
        
        /* Ensure table rows don't break badly */
        tbody tr {{
            page-break-inside: avoid;
        }}
        
        /* Code blocks and ASCII art */
        pre, code {{
            font-family: "Courier New", "Courier", monospace;
            font-size: 8pt;
            background-color: #f5f5f5;
            padding: 8pt;
            border: 1px solid #ddd;
            border-radius: 3pt;
            overflow-x: auto;
            page-break-inside: avoid;
            white-space: pre;
            line-height: 1.3;
        }}
        
        code {{
            padding: 2pt 4pt;
            background-color: #f0f0f0;
        }}
        
        /* Lists */
        ul, ol {{
            margin: 6pt 0 6pt 20pt;
            padding-left: 15pt;
        }}
        
        li {{
            margin: 3pt 0;
        }}
        
        /* Emphasis */
        strong {{
            font-weight: bold;
            color: #1a1a1a;
        }}
        
        em {{
            font-style: italic;
        }}
        
        /* Horizontal rules */
        hr {{
            border: none;
            border-top: 1px solid #ccc;
            margin: 15pt 0;
        }}
        
        /* Block quotes */
        blockquote {{
            margin: 10pt 20pt;
            padding: 8pt 12pt;
            background-color: #f9f9f9;
            border-left: 4px solid #ccc;
            font-style: italic;
        }}
        
        /* Warning boxes */
        .warning {{
            background-color: #fff3cd;
            border: 2px solid #ffc107;
            padding: 10pt;
            margin: 10pt 0;
            border-radius: 4pt;
        }}
        
        /* Page breaks */
        .page-break {{
            page-break-before: always;
        }}
        
        /* Prevent orphans and widows */
        p, li, td, th {{
            orphans: 3;
            widows: 3;
        }}
        
        /* Header styling for ABOUTME comments */
        .aboutme {{
            display: none;
        }}
        
        /* Footnotes */
        .footnote {{
            font-size: 8pt;
            color: #666;
            margin-top: 20pt;
            border-top: 1px solid #ccc;
            padding-top: 8pt;
        }}
    </style>
</head>
<body>
{html_content}
</body>
</html>
"""
    
    # Generate PDF
    output_file = Path(__file__).parent / "executive_summary.pdf"
    HTML(string=full_html).write_pdf(
        output_file,
        stylesheets=[CSS(string="""
            @page {
                size: Letter;
                margin: 0.75in;
            }
        """)]
    )
    
    print(f"✅ PDF generated successfully: {output_file}")
    print(f"📄 File size: {output_file.stat().st_size / 1024:.1f} KB")
    return output_file

if __name__ == "__main__":
    generate_pdf()
