import io, pytest
from pathlib import Path

@pytest.fixture(scope="session")
def mini_pdf(tmp_path_factory):
    """Create a minimal 2-page PDF for testing without requiring an actual PDF file."""
    import fitz
    tmp = tmp_path_factory.mktemp("fixtures")
    pdf_path = tmp / "mini.pdf"
    doc = fitz.open()
    for i in range(2):
        page = doc.new_page()
        page.insert_text((50, 72), f"Page {i+1} content about cathodic protection design per DNV-RP-B401.")
    doc.save(str(pdf_path))
    return pdf_path
