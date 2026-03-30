---
name: pdf-openai-codex-conversion
description: 'Sub-skill of pdf: OpenAI Codex Conversion.'
version: 1.2.2
category: data
type: reference
scripts_exempt: true
---

# OpenAI Codex Conversion

## OpenAI Codex Conversion


**Prerequisites:**
```bash
pip install openai pypdf
export OPENAI_API_KEY="your-api-key-here"
```

**Basic Conversion:**
```python
import openai
from pypdf import PdfReader
from pathlib import Path

def pdf_to_markdown_codex(pdf_path, output_md_path=None, model="gpt-4.1"):
    """
    Convert PDF to markdown using OpenAI Codex.

    Args:
        pdf_path: Path to PDF file
        output_md_path: Optional path for output .md file (auto-generated if None)
        model: OpenAI model to use (gpt-4.1, gpt-4.1-mini, etc.)

    Returns:
        Path to generated markdown file
    """
    # Extract text from PDF
    reader = PdfReader(pdf_path)
    pdf_text = ""

    for page_num, page in enumerate(reader.pages, 1):
        text = page.extract_text()
        pdf_text += f"\n\n--- Page {page_num} ---\n\n{text}"

    # Generate markdown using OpenAI Codex
    client = openai.OpenAI()

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": """You are an expert document converter. Convert the provided PDF text
                to well-structured markdown format. Preserve:
                - Document structure (headings, sections)
                - Lists and bullet points
                - Tables (convert to markdown tables)
                - Code blocks and technical content
                - Links and references

                Format the output as clean, readable markdown."""
            },
            {
                "role": "user",
                "content": f"Convert this PDF text to markdown:\n\n{pdf_text}"
            }
        ],
        temperature=0.3,  # Lower temperature for more consistent formatting
    )

    markdown_content = response.choices[0].message.content

    # Save to file
    if output_md_path is None:
        pdf_stem = Path(pdf_path).stem
        output_md_path = Path(pdf_path).parent / f"{pdf_stem}.md"

    # Ensure parent directory exists
    Path(output_md_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_md_path).write_text(markdown_content, encoding='utf-8')

    return output_md_path

# Usage
md_file = pdf_to_markdown_codex("document.pdf")
print(f"Markdown saved to: {md_file}")
```

**Batch Conversion:**
```python
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def batch_pdf_to_markdown(pdf_directory, output_directory=None, model="gpt-4.1"):
    """
    Convert all PDFs in a directory to markdown.

    Args:
        pdf_directory: Directory containing PDF files
        output_directory: Optional output directory (defaults to pdf_directory/markdown)
        model: OpenAI model to use
    """
    pdf_dir = Path(pdf_directory)

    if output_directory is None:
        output_dir = pdf_dir / "markdown"
    else:
        output_dir = Path(output_directory)

    output_dir.mkdir(parents=True, exist_ok=True)

    pdf_files = list(pdf_dir.glob("*.pdf"))
    total = len(pdf_files)

    logger.info(f"Found {total} PDF files to convert")

    for i, pdf_file in enumerate(pdf_files, 1):
        try:
            output_md = output_dir / f"{pdf_file.stem}.md"

            logger.info(f"[{i}/{total}] Converting {pdf_file.name}...")
            pdf_to_markdown_codex(pdf_file, output_md, model=model)
            logger.info(f"✓ Saved to {output_md.name}")

        except Exception as e:
            logger.error(f"✗ Failed to convert {pdf_file.name}: {e}")

    logger.info(f"\nConversion complete! Files in: {output_dir}")

# Usage
batch_pdf_to_markdown("/path/to/pdfs", model="gpt-4.1")
```

**Chunked Conversion for Large PDFs:**
```python
def pdf_to_markdown_chunked(pdf_path, output_md_path=None,
                            chunk_pages=10, model="gpt-4.1"):
    """
    Convert large PDF by processing in chunks.

    Args:
        pdf_path: Path to PDF file
        output_md_path: Optional output path
        chunk_pages: Number of pages per chunk
        model: OpenAI model to use
    """
    reader = PdfReader(pdf_path)
    total_pages = len(reader.pages)

    markdown_sections = []

    for start_page in range(0, total_pages, chunk_pages):
        end_page = min(start_page + chunk_pages, total_pages)

        # Extract chunk
        chunk_text = ""
        for page_num in range(start_page, end_page):
            text = reader.pages[page_num].extract_text()
            chunk_text += f"\n\n--- Page {page_num + 1} ---\n\n{text}"

        # Convert chunk
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "Convert PDF text to markdown. Maintain structure and formatting."
                },
                {
                    "role": "user",
                    "content": f"Convert pages {start_page + 1}-{end_page} to markdown:\n\n{chunk_text}"
                }
            ],
            temperature=0.3,
        )

        markdown_sections.append(response.choices[0].message.content)
        print(f"Processed pages {start_page + 1}-{end_page}/{total_pages}")

    # Combine sections
    full_markdown = "\n\n---\n\n".join(markdown_sections)

    # Save
    if output_md_path is None:
        output_md_path = Path(pdf_path).with_suffix('.md')

    # Ensure parent directory exists
    Path(output_md_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_md_path).write_text(full_markdown, encoding='utf-8')

    return output_md_path


*Content truncated — see parent skill for full reference.*
