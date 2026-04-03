"""Parser registry for document format handlers."""

from scripts.data.doc_intelligence.parsers.base import BaseParser


def get_parser(filepath: str) -> BaseParser | None:
    """Return first parser that can handle the given file path."""
    from scripts.data.doc_intelligence.parsers.docx_parser import DocxParser
    from scripts.data.doc_intelligence.parsers.html import HtmlParser
    from scripts.data.doc_intelligence.parsers.pdf import PdfParser
    from scripts.data.doc_intelligence.parsers.xlsx import XlsxParser

    parsers = [PdfParser, DocxParser, XlsxParser, HtmlParser]
    for parser_cls in parsers:
        parser = parser_cls()
        if parser.can_handle(filepath):
            return parser
    return None


__all__ = ["BaseParser", "get_parser"]
