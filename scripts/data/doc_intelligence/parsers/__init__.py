"""Parser registry for document format handlers."""

from scripts.data.doc_intelligence.parsers.base import BaseParser
from scripts.data.doc_intelligence.parsers.pdf import PdfParser
from scripts.data.doc_intelligence.parsers.docx_parser import DocxParser
from scripts.data.doc_intelligence.parsers.xlsx import XlsxParser

PARSERS = [PdfParser, DocxParser, XlsxParser]


def get_parser(filepath: str) -> BaseParser | None:
    """Return first parser that can handle the given file path."""
    for parser_cls in PARSERS:
        parser = parser_cls()
        if parser.can_handle(filepath):
            return parser
    return None
