#!/usr/bin/env python3
"""
Tests for document parsers
"""

import unittest
from pathlib import Path
import tempfile
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from doc_to_context import (
    PDFParser, WordParser, ExcelParser, HTMLParser,
    DocumentToContextConverter
)


class TestParserSelection(unittest.TestCase):
    """Test parser selection logic."""

    def test_pdf_parser_selection(self):
        """Test PDF parser can handle PDF files."""
        self.assertTrue(PDFParser.can_handle('application/pdf', '.pdf'))
        self.assertFalse(PDFParser.can_handle('text/html', '.html'))

    def test_word_parser_selection(self):
        """Test Word parser can handle DOCX files."""
        self.assertTrue(WordParser.can_handle(
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.docx'
        ))
        self.assertFalse(WordParser.can_handle('application/pdf', '.pdf'))

    def test_excel_parser_selection(self):
        """Test Excel parser can handle XLSX files."""
        self.assertTrue(ExcelParser.can_handle(
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.xlsx'
        ))
        self.assertTrue(ExcelParser.can_handle('', '.xlsx'))
        self.assertFalse(ExcelParser.can_handle('text/html', '.html'))

    def test_html_parser_selection(self):
        """Test HTML parser can handle HTML files."""
        self.assertTrue(HTMLParser.can_handle('text/html', '.html'))
        self.assertTrue(HTMLParser.can_handle('', '.htm'))
        self.assertFalse(HTMLParser.can_handle('application/pdf', '.pdf'))


class TestTableConversion(unittest.TestCase):
    """Test table to markdown conversion."""

    def test_simple_table(self):
        """Test conversion of simple table."""
        table_data = [
            ['Header 1', 'Header 2', 'Header 3'],
            ['Row 1 Col 1', 'Row 1 Col 2', 'Row 1 Col 3'],
            ['Row 2 Col 1', 'Row 2 Col 2', 'Row 2 Col 3']
        ]

        markdown = PDFParser._table_to_markdown(table_data)

        self.assertIn('Header 1', markdown)
        self.assertIn('---', markdown)
        self.assertIn('Row 1 Col 1', markdown)

    def test_empty_table(self):
        """Test handling of empty table."""
        table_data = []
        markdown = PDFParser._table_to_markdown(table_data)
        self.assertEqual(markdown, "")

    def test_table_with_empty_cells(self):
        """Test table with None/empty cells."""
        table_data = [
            ['A', 'B', 'C'],
            ['1', None, '3'],
            [None, '2', None]
        ]

        markdown = PDFParser._table_to_markdown(table_data)
        self.assertIn('|', markdown)
        self.assertIn('A', markdown)


class TestHTMLParser(unittest.TestCase):
    """Test HTML parsing functionality."""

    def test_simple_html_parsing(self):
        """Test parsing simple HTML document."""
        html_content = """
        <html>
            <head><title>Test Document</title></head>
            <body>
                <h1>Main Heading</h1>
                <p>This is a paragraph.</p>
                <table>
                    <tr><th>Col1</th><th>Col2</th></tr>
                    <tr><td>Data1</td><td>Data2</td></tr>
                </table>
                <a href="https://example.com">Example Link</a>
            </body>
        </html>
        """

        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            f.write(html_content)
            temp_path = Path(f.name)

        try:
            parser = HTMLParser()
            content = parser.parse(temp_path)

            self.assertEqual(content.metadata.format, 'HTML')
            self.assertIn('Main Heading', content.text)
            self.assertEqual(len(content.tables), 1)
            self.assertEqual(len(content.links), 1)
            self.assertEqual(content.links[0]['url'], 'https://example.com')
        finally:
            temp_path.unlink()


class TestConverterIntegration(unittest.TestCase):
    """Test document converter integration."""

    def test_html_to_markdown_conversion(self):
        """Test full HTML to markdown conversion."""
        html_content = """
        <html>
            <head><title>Integration Test</title></head>
            <body>
                <h1>Test Document</h1>
                <p>Content paragraph.</p>
            </body>
        </html>
        """

        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            f.write(html_content)
            temp_html = Path(f.name)

        temp_output = temp_html.with_suffix('.context.md')

        try:
            converter = DocumentToContextConverter()
            converter.convert(str(temp_html))

            self.assertTrue(temp_output.exists())

            # Check output content
            with open(temp_output, 'r') as f:
                output = f.read()
                self.assertIn('Document Metadata', output)
                self.assertIn('Integration Test', output)
                self.assertIn('Test Document', output)
        finally:
            temp_html.unlink()
            if temp_output.exists():
                temp_output.unlink()


if __name__ == '__main__':
    unittest.main()
