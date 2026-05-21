"""Follow-up tests for source_doc_key threading across the six remaining
promoters (curves, definitions, procedures, requirements, tables,
worked_examples) — completes acceptance criterion for #2389.

The first wave (constants, equations) is covered in
``test_promoter_source_doc_key.py``. This module mirrors the same contract:

- Rendered promoted artifacts emit ``# content-hash: <sha256>`` and
  ``# source_doc_key: <algo>:<hex>`` headers.
- Promoters fail closed when ``source.doc_key`` is missing, empty, or
  non-canonical (bare hex, unknown algorithm, wrong hex length, uppercase
  hex, filename, absolute filesystem path, self-loop against the rendered
  body hash).
- No filesystem path or raw client filename leaks into the header value.
- The content-hash semantics are unchanged (still a sha256 of the body).
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest


SHA256_A = "sha256:" + "a" * 64
SHA256_B = "sha256:" + "b" * 64
SHA256_C = "sha256:" + "c" * 64


# ── shared assertion helpers ──────────────────────────────────────────────


def _assert_content_hash_header(text: str) -> str:
    """Find the canonical ``# content-hash: <hex>`` line and return the hex."""
    for line in text.splitlines():
        m = re.match(r"^#\s*content-hash:\s*([0-9a-f]{64})\s*$", line)
        if m:
            return m.group(1)
    raise AssertionError(
        "no canonical '# content-hash: <64-hex>' header in output:\n"
        f"{text[:400]}"
    )


def _assert_source_doc_key_header(text: str, expected: str) -> None:
    needle = f"# source_doc_key: {expected}"
    assert needle in text, (
        f"expected header line {needle!r} missing; output head:\n{text[:400]}"
    )


def _assert_no_path_leakage_in_doc_key_headers(text: str) -> None:
    """No `# source_doc_key:` line may contain a path separator."""
    sdk_lines = [
        ln for ln in text.splitlines() if ln.startswith("# source_doc_key:")
    ]
    assert sdk_lines, (
        "expected at least one # source_doc_key header; "
        f"output head:\n{text[:400]}"
    )
    for ln in sdk_lines:
        value = ln.split(":", 1)[1].strip()
        # value is "<algo>:<hex>" — algorithm separator is ':', not '/'\\
        assert "/" not in value, value
        assert "\\" not in value, value


# ── record-builder fixtures (per-promoter shapes) ─────────────────────────


def _curve_record(
    *,
    doc_key: str | None = SHA256_A,
    caption: str = "S-N Curve for Tubular Joints in Seawater",
    figure_id: str = "Figure 4.1",
    domain: str = "naval-architecture",
    document: str = "DNV-RP-C203.pdf",
    page: int = 22,
) -> dict:
    source: dict = {"document": document, "page": page}
    if doc_key is not None:
        source["doc_key"] = doc_key
    return {
        "caption": caption,
        "figure_id": figure_id,
        "source": source,
        "domain": domain,
        "manifest": document,
    }


def _definition_record(
    *,
    doc_key: str | None = SHA256_A,
    text: str = (
        "Cathodic Protection (CP): A technique used to control corrosion "
        "by making the metal surface the cathode of an electrochemical cell."
    ),
    domain: str = "naval-architecture",
    document: str = "DNV-RP-B401.pdf",
    section: str = "1.3",
    page: int = 5,
) -> dict:
    source: dict = {"document": document, "section": section, "page": page}
    if doc_key is not None:
        source["doc_key"] = doc_key
    return {
        "text": text,
        "source": source,
        "domain": domain,
        "manifest": document,
    }


def _procedure_record(
    *,
    doc_key: str | None = SHA256_A,
    text: str = (
        "Procedure: Cathodic Protection Survey\n"
        "1. Verify reference electrode calibration\n"
        "2. Measure potential at each test point\n"
        "3. Record readings against Ag/AgCl reference"
    ),
    domain: str = "naval-architecture",
    document: str = "DNV-RP-B401.pdf",
    section: str = "8.2",
    page: int = 55,
) -> dict:
    source: dict = {"document": document, "section": section, "page": page}
    if doc_key is not None:
        source["doc_key"] = doc_key
    return {
        "text": text,
        "source": source,
        "domain": domain,
        "manifest": document,
    }


def _requirement_record(
    *,
    doc_key: str | None = SHA256_A,
    text: str = (
        "The minimum design life for cathodic protection systems shall be "
        "25 years unless otherwise specified by the operator."
    ),
    domain: str = "naval-architecture",
    document: str = "DNV-RP-B401.pdf",
    section: str = "4.1.2",
    page: int = 10,
) -> dict:
    source: dict = {"document": document, "section": section, "page": page}
    if doc_key is not None:
        source["doc_key"] = doc_key
    return {
        "text": text,
        "source": source,
        "domain": domain,
        "manifest": document,
    }


def _table_record(
    *,
    project_root: Path,
    doc_key: str | None = SHA256_A,
    csv_basename: str = "Sample-Table-0.csv",
    domain: str = "naval-architecture",
    document: str = "Sample.pdf",
    csv_body: str = "Material,Yield (MPa)\nS355,355\nS460,460\n",
) -> dict:
    """Create a table record AND lay down the upstream source CSV the
    tables promoter expects to find under
    ``{project_root}/data/doc-intelligence/tables/<csv_basename>``.
    """
    src = project_root / "data" / "doc-intelligence" / "tables" / csv_basename
    src.parent.mkdir(parents=True, exist_ok=True)
    src.write_text(csv_body, encoding="utf-8")

    source: dict = {"document": document, "page": 12}
    if doc_key is not None:
        source["doc_key"] = doc_key
    return {
        "title": "Material Properties",
        "columns": ["Material", "Yield (MPa)"],
        "row_count": 2,
        "csv_path": f"tables/{csv_basename}",
        "source": source,
        "domain": domain,
        "manifest": document,
    }


def _worked_example_record(
    *,
    doc_key: str | None = SHA256_A,
    text: str = (
        "Example 3.1: Calculate hydrostatic pressure at 100m depth.\n"
        "Given: rho = 1025 kg/m³, g = 9.81 m/s², d = 100 m\n"
        "Solution: P = 1025 × 9.81 × 100 = 1,005,525 Pa"
    ),
    domain: str = "naval-architecture",
    document: str = "DNV-RP-C205.pdf",
    section: str = "3.3",
    page: int = 18,
) -> dict:
    source: dict = {"document": document, "section": section, "page": page}
    if doc_key is not None:
        source["doc_key"] = doc_key
    return {
        "text": text,
        "source": source,
        "domain": domain,
        "manifest": document,
    }


# ── invariant test cohorts ────────────────────────────────────────────────
#
# Every promoter gets the same shape of tests. We keep them as discrete
# classes (rather than parametrize across a single class) so failure
# diagnostics point at the exact promoter family.


class TestCurvesPromoterSourceDocKey:
    """Verify the curves promoter emits and validates source_doc_key."""

    def test_emits_both_headers_on_scaffold(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.curves import (
            promote_curves,
        )

        result = promote_curves([_curve_record(doc_key=SHA256_A)], tmp_dir)

        assert result.errors == [], f"unexpected errors: {result.errors}"
        py_paths = [
            p for p in result.files_written if p.endswith("curves.py")
        ]
        assert py_paths, "expected at least one curves.py output"
        out_text = Path(py_paths[0]).read_text(encoding="utf-8")
        _assert_content_hash_header(out_text)
        _assert_source_doc_key_header(out_text, SHA256_A)
        _assert_no_path_leakage_in_doc_key_headers(out_text)

    def test_emits_both_headers_on_placeholder_csv(self, tmp_dir):
        """Placeholder CSV files are also promoted artifacts; per the contract
        they must carry the same provenance headers."""
        from scripts.data.doc_intelligence.promoters.curves import (
            promote_curves,
        )

        result = promote_curves([_curve_record(doc_key=SHA256_A)], tmp_dir)
        csv_paths = [p for p in result.files_written if p.endswith(".csv")]
        assert csv_paths, "expected at least one placeholder CSV"
        out_text = Path(csv_paths[0]).read_text(encoding="utf-8")
        _assert_content_hash_header(out_text)
        _assert_source_doc_key_header(out_text, SHA256_A)

    def test_fails_closed_when_doc_key_missing(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.curves import (
            promote_curves,
        )

        result = promote_curves([_curve_record(doc_key=None)], tmp_dir)
        assert result.errors, "expected fail-closed for missing source.doc_key"
        assert result.files_written == []

    def test_fails_closed_on_malformed_doc_key(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.curves import (
            promote_curves,
        )

        result = promote_curves(
            [_curve_record(doc_key="not-a-hash")], tmp_dir,
        )
        assert result.errors
        assert result.files_written == []

    def test_fails_closed_on_filename_doc_key(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.curves import (
            promote_curves,
        )

        result = promote_curves(
            [_curve_record(doc_key="DNV-RP-C205.pdf")], tmp_dir,
        )
        assert result.errors
        assert result.files_written == []

    def test_fails_closed_on_path_doc_key(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.curves import (
            promote_curves,
        )

        result = promote_curves(
            [_curve_record(doc_key="/mnt/ace/acma-codes/foo.pdf")], tmp_dir,
        )
        assert result.errors
        assert result.files_written == []


class TestDefinitionsPromoterSourceDocKey:
    """Verify the definitions promoter emits canonical headers and validates."""

    def test_emits_canonical_content_hash_header(self, tmp_dir):
        """Definitions must emit ``# content-hash:`` (dash) per contract,
        replacing the legacy ``# content_hash:`` (underscore) field."""
        from scripts.data.doc_intelligence.promoters.definitions import (
            promote_definitions,
        )

        result = promote_definitions(
            [_definition_record(doc_key=SHA256_A)], tmp_dir,
        )
        assert result.errors == [], f"unexpected errors: {result.errors}"
        assert result.files_written, "expected glossary.yaml to be written"
        out_text = Path(result.files_written[0]).read_text(encoding="utf-8")
        _assert_content_hash_header(out_text)

    def test_emits_source_doc_key_header(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.definitions import (
            promote_definitions,
        )

        result = promote_definitions(
            [_definition_record(doc_key=SHA256_A)], tmp_dir,
        )
        out_text = Path(result.files_written[0]).read_text(encoding="utf-8")
        _assert_source_doc_key_header(out_text, SHA256_A)
        _assert_no_path_leakage_in_doc_key_headers(out_text)

    def test_fails_closed_when_doc_key_missing(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.definitions import (
            promote_definitions,
        )

        result = promote_definitions(
            [_definition_record(doc_key=None)], tmp_dir,
        )
        assert result.errors
        assert result.files_written == []

    def test_fails_closed_on_malformed_doc_key(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.definitions import (
            promote_definitions,
        )

        result = promote_definitions(
            [_definition_record(doc_key="not-canonical")], tmp_dir,
        )
        assert result.errors
        assert result.files_written == []

    def test_fails_closed_on_path_doc_key(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.definitions import (
            promote_definitions,
        )

        result = promote_definitions(
            [_definition_record(doc_key="/mnt/ace/x.pdf")], tmp_dir,
        )
        assert result.errors
        assert result.files_written == []


class TestProceduresPromoterSourceDocKey:
    """Verify the procedures promoter emits canonical comment headers."""

    def test_emits_both_headers_in_yaml(self, tmp_dir):
        """YAML output must carry ``# content-hash:`` and ``# source_doc_key:``
        comment-form headers per contract section 8.3."""
        from scripts.data.doc_intelligence.promoters.procedures import (
            promote_procedures,
        )

        result = promote_procedures(
            [_procedure_record(doc_key=SHA256_A)], tmp_dir,
        )
        assert result.errors == [], f"unexpected errors: {result.errors}"
        assert result.files_written, "expected procedure YAML to be written"
        out_text = Path(result.files_written[0]).read_text(encoding="utf-8")
        _assert_content_hash_header(out_text)
        _assert_source_doc_key_header(out_text, SHA256_A)
        _assert_no_path_leakage_in_doc_key_headers(out_text)

    def test_fails_closed_when_doc_key_missing(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.procedures import (
            promote_procedures,
        )

        result = promote_procedures(
            [_procedure_record(doc_key=None)], tmp_dir,
        )
        assert result.errors
        assert result.files_written == []

    def test_fails_closed_on_malformed_doc_key(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.procedures import (
            promote_procedures,
        )

        result = promote_procedures(
            [_procedure_record(doc_key="bad")], tmp_dir,
        )
        assert result.errors
        assert result.files_written == []

    def test_fails_closed_on_filename_doc_key(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.procedures import (
            promote_procedures,
        )

        result = promote_procedures(
            [_procedure_record(doc_key="proc.pdf")], tmp_dir,
        )
        assert result.errors
        assert result.files_written == []


class TestRequirementsPromoterSourceDocKey:
    """Verify the requirements promoter threads source_doc_key."""

    def test_emits_both_headers(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.requirements import (
            promote_requirements,
        )

        result = promote_requirements(
            [_requirement_record(doc_key=SHA256_A)], tmp_dir,
        )
        assert result.errors == [], f"unexpected errors: {result.errors}"
        assert result.files_written, "expected requirements.py to be written"
        out_text = Path(result.files_written[0]).read_text(encoding="utf-8")
        _assert_content_hash_header(out_text)
        _assert_source_doc_key_header(out_text, SHA256_A)
        _assert_no_path_leakage_in_doc_key_headers(out_text)

    def test_multiple_distinct_doc_keys_all_emitted(self, tmp_dir):
        """Grouped requirements module aggregates per-record sources; every
        distinct source_doc_key must appear."""
        from scripts.data.doc_intelligence.promoters.requirements import (
            promote_requirements,
        )

        recs = [
            _requirement_record(
                text="The minimum design life shall be 25 years.",
                doc_key=SHA256_A,
            ),
            _requirement_record(
                text=(
                    "All structural steel shall comply with EN 10025 Grade "
                    "S355 or equivalent."
                ),
                doc_key=SHA256_B,
                document="EN-10025.pdf",
            ),
        ]
        result = promote_requirements(recs, tmp_dir)
        assert result.errors == [], f"unexpected errors: {result.errors}"
        out_text = Path(result.files_written[0]).read_text(encoding="utf-8")
        assert SHA256_A in out_text
        assert SHA256_B in out_text

    def test_fails_closed_when_doc_key_missing(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.requirements import (
            promote_requirements,
        )

        result = promote_requirements(
            [_requirement_record(doc_key=None)], tmp_dir,
        )
        assert result.errors
        assert result.files_written == []

    def test_fails_closed_on_malformed_doc_key(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.requirements import (
            promote_requirements,
        )

        result = promote_requirements(
            [_requirement_record(doc_key="garbage")], tmp_dir,
        )
        assert result.errors
        assert result.files_written == []


class TestTablesPromoterSourceDocKey:
    """Verify the tables promoter prepends headers to copied CSVs."""

    def test_emits_both_headers_at_csv_head(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.tables import (
            promote_tables,
        )

        rec = _table_record(project_root=tmp_dir, doc_key=SHA256_A)
        result = promote_tables([rec], tmp_dir)
        assert result.errors == [], f"unexpected errors: {result.errors}"
        assert result.files_written, "expected promoted CSV to be written"
        out_text = Path(result.files_written[0]).read_text(encoding="utf-8")
        _assert_content_hash_header(out_text)
        _assert_source_doc_key_header(out_text, SHA256_A)
        # Original CSV body must still be present after the header block.
        assert "Material,Yield (MPa)" in out_text
        assert "S355,355" in out_text

    def test_csv_headers_precede_data(self, tmp_dir):
        """Headers must appear BEFORE the first non-comment data line, so
        comment-aware parsers (pandas comment='#') skip them naturally."""
        from scripts.data.doc_intelligence.promoters.tables import (
            promote_tables,
        )

        rec = _table_record(project_root=tmp_dir, doc_key=SHA256_A)
        result = promote_tables([rec], tmp_dir)
        out_text = Path(result.files_written[0]).read_text(encoding="utf-8")
        non_comment_lines = [
            ln for ln in out_text.splitlines() if not ln.startswith("#")
        ]
        assert non_comment_lines[0].startswith("Material"), (
            "expected first non-comment line to be the original CSV header"
        )

    def test_fails_closed_when_doc_key_missing(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.tables import (
            promote_tables,
        )

        rec = _table_record(project_root=tmp_dir, doc_key=None)
        result = promote_tables([rec], tmp_dir)
        assert result.errors
        assert result.files_written == []

    def test_fails_closed_on_malformed_doc_key(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.tables import (
            promote_tables,
        )

        rec = _table_record(project_root=tmp_dir, doc_key="bad")
        result = promote_tables([rec], tmp_dir)
        assert result.errors
        assert result.files_written == []

    def test_fails_closed_on_path_doc_key(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.tables import (
            promote_tables,
        )

        rec = _table_record(
            project_root=tmp_dir, doc_key="/mnt/ace/acma-codes/x.csv",
        )
        result = promote_tables([rec], tmp_dir)
        assert result.errors
        assert result.files_written == []


class TestWorkedExamplesPromoterSourceDocKey:
    """Verify the worked-examples promoter threads source_doc_key."""

    def test_emits_both_headers(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.worked_examples import (
            promote_worked_examples,
        )

        result = promote_worked_examples(
            [_worked_example_record(doc_key=SHA256_A)], tmp_dir,
        )
        assert result.errors == [], f"unexpected errors: {result.errors}"
        assert result.files_written, "expected test_*.py to be written"
        out_text = Path(result.files_written[0]).read_text(encoding="utf-8")
        _assert_content_hash_header(out_text)
        _assert_source_doc_key_header(out_text, SHA256_A)
        _assert_no_path_leakage_in_doc_key_headers(out_text)

    def test_multiple_distinct_doc_keys_all_emitted(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.worked_examples import (
            promote_worked_examples,
        )

        recs = [
            _worked_example_record(doc_key=SHA256_A),
            _worked_example_record(
                text=(
                    "Example 5.2: Determine buoyancy on 2m³ object.\n"
                    "Given: rho = 1025 kg/m³, g = 9.81 m/s², V = 2 m³\n"
                    "Solution: F_b = 1025 × 9.81 × 2 = 20,110.5 N"
                ),
                doc_key=SHA256_B,
            ),
        ]
        result = promote_worked_examples(recs, tmp_dir)
        assert result.errors == [], f"unexpected errors: {result.errors}"
        out_text = Path(result.files_written[0]).read_text(encoding="utf-8")
        assert SHA256_A in out_text
        assert SHA256_B in out_text

    def test_fails_closed_when_doc_key_missing(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.worked_examples import (
            promote_worked_examples,
        )

        result = promote_worked_examples(
            [_worked_example_record(doc_key=None)], tmp_dir,
        )
        assert result.errors
        assert result.files_written == []

    def test_fails_closed_on_malformed_doc_key(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.worked_examples import (
            promote_worked_examples,
        )

        result = promote_worked_examples(
            [_worked_example_record(doc_key="bad")], tmp_dir,
        )
        assert result.errors
        assert result.files_written == []

    def test_fails_closed_on_filename_doc_key(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.worked_examples import (
            promote_worked_examples,
        )

        result = promote_worked_examples(
            [_worked_example_record(doc_key="DNV-RP-C205.pdf")], tmp_dir,
        )
        assert result.errors
        assert result.files_written == []


# ── self-loop guard parametrized across all six families ──────────────────


@pytest.mark.parametrize(
    "family",
    [
        "curves",
        "definitions",
        "procedures",
        "requirements",
        "tables",
        "worked_examples",
    ],
)
def test_self_loop_doc_key_rejected(family: str, tmp_dir: Path) -> None:
    """For any promoter family, a record whose source_doc_key equals
    ``sha256:<own-output-content-hash>`` must be rejected on the second pass.

    We run the promoter twice: first with a benign doc_key to learn the
    output's content-hash; then with that hash as the doc_key. The second
    pass must fail closed.
    """
    if family == "curves":
        from scripts.data.doc_intelligence.promoters.curves import (
            promote_curves as promote,
        )
        first_rec = _curve_record(doc_key=SHA256_A)
        rebuild = _curve_record
    elif family == "definitions":
        from scripts.data.doc_intelligence.promoters.definitions import (
            promote_definitions as promote,
        )
        first_rec = _definition_record(doc_key=SHA256_A)
        rebuild = _definition_record
    elif family == "procedures":
        from scripts.data.doc_intelligence.promoters.procedures import (
            promote_procedures as promote,
        )
        first_rec = _procedure_record(doc_key=SHA256_A)
        rebuild = _procedure_record
    elif family == "requirements":
        from scripts.data.doc_intelligence.promoters.requirements import (
            promote_requirements as promote,
        )
        first_rec = _requirement_record(doc_key=SHA256_A)
        rebuild = _requirement_record
    elif family == "tables":
        from scripts.data.doc_intelligence.promoters.tables import (
            promote_tables as promote,
        )
        first_rec = _table_record(
            project_root=tmp_dir / "first", doc_key=SHA256_A,
        )
        def rebuild(*, doc_key):
            return _table_record(
                project_root=tmp_dir / "second", doc_key=doc_key,
            )
    elif family == "worked_examples":
        from scripts.data.doc_intelligence.promoters.worked_examples import (
            promote_worked_examples as promote,
        )
        first_rec = _worked_example_record(doc_key=SHA256_A)
        rebuild = _worked_example_record
    else:  # pragma: no cover
        raise AssertionError(f"unknown family {family}")

    first_root = tmp_dir / "first"
    first_root.mkdir(exist_ok=True)
    result1 = promote([first_rec], first_root)
    assert result1.files_written, (
        f"first pass for {family} produced no output: {result1.errors}"
    )

    text = Path(result1.files_written[0]).read_text(encoding="utf-8")
    body_hex = _assert_content_hash_header(text)
    loop_key = f"sha256:{body_hex}"

    second_root = tmp_dir / "second"
    second_root.mkdir(exist_ok=True)
    loop_rec = rebuild(doc_key=loop_key)
    result2 = promote([loop_rec], second_root)
    assert result2.errors, (
        f"{family}: self-loop doc_key {loop_key!r} should have been rejected, "
        f"but promoter wrote: {result2.files_written}"
    )
    assert result2.files_written == []
