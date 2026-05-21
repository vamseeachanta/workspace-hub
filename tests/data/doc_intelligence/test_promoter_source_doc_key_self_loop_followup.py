"""Focused source_doc_key promoter follow-up tests (#2389)."""

from pathlib import Path

import pytest

from tests.data.doc_intelligence.promoter_source_doc_key_helpers import *



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
