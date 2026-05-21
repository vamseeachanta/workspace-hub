"""Tests for source_doc_key threading through the promotion pipeline (#2389).

Covers:
- Canonical-form validator (`validate_source_doc_key` in text_utils)
- Constants promoter integration (single-output module)
- Equations promoter integration (grouped multi-output modules)
- Fail-closed semantics for missing/malformed/ambiguous source identity
- Self-loop guard (source_doc_key must not equal the output's own content-hash)
- Leakage guards (no literal filesystem paths or raw filenames)
- Preservation of existing content-hash semantics
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest


SHA256_A = "sha256:" + "a" * 64
SHA256_B = "sha256:" + "b" * 64
SHA256_C = "sha256:" + "c" * 64


# ── helpers ────────────────────────────────────────────────────────────


def _const_record(
    text: str = "Steel yield strength = 355 MPa for Grade S355.",
    doc_key: str | None = SHA256_A,
    document: str = "src.pdf",
    section: str = "1.0",
    page: int = 1,
    domain: str = "naval-architecture",
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


def _eq_record(
    text: str = (
        "Hydrostatic pressure: P = rho * g * d, where rho is fluid density "
        "[kg/m³], g is gravitational acceleration [m/s²], d is depth [m]. "
        "Returns pressure in Pa."
    ),
    doc_key: str | None = SHA256_A,
    domain: str = "naval-architecture",
    document: str = "src.pdf",
) -> dict:
    source: dict = {"document": document, "section": "3.2", "page": 15}
    if doc_key is not None:
        source["doc_key"] = doc_key
    return {
        "text": text,
        "source": source,
        "domain": domain,
        "manifest": document,
    }


# ── validator unit tests ───────────────────────────────────────────────


class TestValidateSourceDocKey:
    """Direct tests of the canonical-form validator."""

    def test_accepts_sha256(self):
        from scripts.data.doc_intelligence.promoters.text_utils import (
            validate_source_doc_key,
        )
        v = "sha256:" + "0" * 64
        assert validate_source_doc_key(v) == v

    def test_accepts_sha512(self):
        from scripts.data.doc_intelligence.promoters.text_utils import (
            validate_source_doc_key,
        )
        v = "sha512:" + "f" * 128
        assert validate_source_doc_key(v) == v

    def test_accepts_md5(self):
        from scripts.data.doc_intelligence.promoters.text_utils import (
            validate_source_doc_key,
        )
        v = "md5:" + "1" * 32
        assert validate_source_doc_key(v) == v

    def test_accepts_sha1(self):
        from scripts.data.doc_intelligence.promoters.text_utils import (
            validate_source_doc_key,
        )
        v = "sha1:" + "2" * 40
        assert validate_source_doc_key(v) == v

    def test_rejects_none(self):
        from scripts.data.doc_intelligence.promoters.text_utils import (
            SourceDocKeyError,
            validate_source_doc_key,
        )
        with pytest.raises(SourceDocKeyError):
            validate_source_doc_key(None)

    def test_rejects_empty_string(self):
        from scripts.data.doc_intelligence.promoters.text_utils import (
            SourceDocKeyError,
            validate_source_doc_key,
        )
        with pytest.raises(SourceDocKeyError):
            validate_source_doc_key("")

    def test_rejects_bare_hex_no_algorithm(self):
        from scripts.data.doc_intelligence.promoters.text_utils import (
            SourceDocKeyError,
            validate_source_doc_key,
        )
        with pytest.raises(SourceDocKeyError):
            validate_source_doc_key("a" * 64)

    def test_rejects_unknown_algorithm(self):
        from scripts.data.doc_intelligence.promoters.text_utils import (
            SourceDocKeyError,
            validate_source_doc_key,
        )
        with pytest.raises(SourceDocKeyError):
            validate_source_doc_key("blake3:" + "a" * 64)

    def test_rejects_wrong_hex_length_sha256(self):
        from scripts.data.doc_intelligence.promoters.text_utils import (
            SourceDocKeyError,
            validate_source_doc_key,
        )
        with pytest.raises(SourceDocKeyError):
            validate_source_doc_key("sha256:" + "a" * 32)

    def test_rejects_uppercase_hex(self):
        from scripts.data.doc_intelligence.promoters.text_utils import (
            SourceDocKeyError,
            validate_source_doc_key,
        )
        with pytest.raises(SourceDocKeyError):
            validate_source_doc_key("sha256:" + "A" * 64)

    def test_rejects_filename_as_doc_key(self):
        """A raw filename like 'DNV-RP-C205.pdf' is not a canonical doc_key."""
        from scripts.data.doc_intelligence.promoters.text_utils import (
            SourceDocKeyError,
            validate_source_doc_key,
        )
        with pytest.raises(SourceDocKeyError):
            validate_source_doc_key("DNV-RP-C205.pdf")

    def test_rejects_absolute_filesystem_path(self):
        """Literal /mnt/ace paths must never be accepted as doc_key."""
        from scripts.data.doc_intelligence.promoters.text_utils import (
            SourceDocKeyError,
            validate_source_doc_key,
        )
        with pytest.raises(SourceDocKeyError):
            validate_source_doc_key("/mnt/ace/acma-codes/foo.pdf")

    def test_rejects_windows_style_path(self):
        from scripts.data.doc_intelligence.promoters.text_utils import (
            SourceDocKeyError,
            validate_source_doc_key,
        )
        with pytest.raises(SourceDocKeyError):
            validate_source_doc_key(r"D:\workspace-hub\foo.pdf")

    def test_rejects_self_loop_against_output_hash(self):
        """source_doc_key must not equal sha256:<output-content-hash>."""
        from scripts.data.doc_intelligence.promoters.text_utils import (
            SourceDocKeyError,
            validate_source_doc_key,
        )
        body_hash_hex = "a" * 64
        with pytest.raises(SourceDocKeyError):
            validate_source_doc_key(
                f"sha256:{body_hash_hex}", output_content_hash=body_hash_hex
            )

    def test_accepts_non_self_loop_with_output_hash(self):
        from scripts.data.doc_intelligence.promoters.text_utils import (
            validate_source_doc_key,
        )
        body_hash_hex = "a" * 64
        v = "sha256:" + "b" * 64
        assert (
            validate_source_doc_key(v, output_content_hash=body_hash_hex) == v
        )


# ── constants promoter integration ─────────────────────────────────────


class TestConstantsPromoterSourceDocKey:
    """Verify the constants promoter emits and validates source_doc_key."""

    def test_emits_source_doc_key_header(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.constants import (
            promote_constants,
        )
        rec = _const_record(
            text="Steel yield strength = 355 MPa.", doc_key=SHA256_A
        )
        result = promote_constants([rec], tmp_dir)
        assert result.errors == [], f"unexpected errors: {result.errors}"
        assert len(result.files_written) == 1
        out_text = Path(result.files_written[0]).read_text()
        assert f"# source_doc_key: {SHA256_A}" in out_text

    def test_preserves_content_hash_header(self, tmp_dir):
        """The existing # content-hash: header must still be the first line
        with a 64-char hex digest of the body."""
        from scripts.data.doc_intelligence.promoters.constants import (
            promote_constants,
        )
        rec = _const_record(
            text="Seawater density = 1025 kg/m³.", doc_key=SHA256_A
        )
        result = promote_constants([rec], tmp_dir)
        out_text = Path(result.files_written[0]).read_text()
        first_line = out_text.split("\n", 1)[0]
        assert first_line.startswith("# content-hash: ")
        hex_part = first_line[len("# content-hash: "):]
        assert re.fullmatch(r"[0-9a-f]{64}", hex_part), hex_part

    def test_fails_closed_when_doc_key_missing(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.constants import (
            promote_constants,
        )
        rec = _const_record(doc_key=None)
        result = promote_constants([rec], tmp_dir)
        assert result.errors, "expected fail-closed for missing source.doc_key"
        assert result.files_written == []

    def test_fails_closed_when_doc_key_empty_string(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.constants import (
            promote_constants,
        )
        rec = _const_record(doc_key="")
        result = promote_constants([rec], tmp_dir)
        assert result.errors
        assert result.files_written == []

    def test_fails_closed_on_malformed_doc_key(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.constants import (
            promote_constants,
        )
        rec = _const_record(doc_key="not-a-hash")
        result = promote_constants([rec], tmp_dir)
        assert result.errors
        assert result.files_written == []

    def test_fails_closed_on_literal_path_doc_key(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.constants import (
            promote_constants,
        )
        rec = _const_record(doc_key="/mnt/ace/acma-codes/foo.pdf")
        result = promote_constants([rec], tmp_dir)
        assert result.errors
        assert result.files_written == []

    def test_fails_closed_on_filename_doc_key(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.constants import (
            promote_constants,
        )
        rec = _const_record(doc_key="DNV-RP-C205.pdf")
        result = promote_constants([rec], tmp_dir)
        assert result.errors
        assert result.files_written == []

    def test_fails_closed_on_self_loop(self, tmp_dir):
        """If a record's source_doc_key happens to equal sha256:<output body
        hash>, the promoter must refuse to write."""
        from scripts.data.doc_intelligence.promoters.constants import (
            promote_constants,
        )
        # First pass with a benign doc_key to learn the body hash
        first = promote_constants(
            [_const_record(text="K = 1 m.", doc_key=SHA256_A)],
            tmp_dir / "first",
        )
        assert first.files_written, first.errors
        out_text = Path(first.files_written[0]).read_text()
        body_hash_hex = (
            out_text.split("\n", 1)[0][len("# content-hash: "):]
        )
        loop_key = f"sha256:{body_hash_hex}"
        loop_rec = _const_record(text="K = 1 m.", doc_key=loop_key)
        result = promote_constants([loop_rec], tmp_dir / "second")
        assert result.errors, (
            "self-loop source_doc_key must be rejected, "
            f"but promoter wrote: {result.files_written}"
        )
        assert result.files_written == []

    def test_no_repo_path_leakage_in_output(self, tmp_dir):
        """Promoted artifact must not contain /mnt/ace or raw client paths
        even when records reference them in source.document."""
        from scripts.data.doc_intelligence.promoters.constants import (
            promote_constants,
        )
        rec = _const_record(
            text="K = 1 m.",
            doc_key=SHA256_A,
            document="public-name.pdf",
        )
        result = promote_constants([rec], tmp_dir)
        out_text = Path(result.files_written[0]).read_text()
        assert "/mnt/ace" not in out_text
        # Source-doc-key never carries a path
        sdk_lines = [
            ln for ln in out_text.splitlines()
            if ln.startswith("# source_doc_key:")
        ]
        assert sdk_lines, "expected at least one source_doc_key header"
        for ln in sdk_lines:
            value = ln.split(": ", 1)[1].strip()
            assert "/" not in value and "\\" not in value, value


# ── equations promoter integration ─────────────────────────────────────


class TestEquationsPromoterSourceDocKey:
    """Verify the grouped equations promoter threads source_doc_key."""

    def test_emits_source_doc_key_in_module(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.equations import (
            promote_equations,
        )
        rec = _eq_record(doc_key=SHA256_A)
        result = promote_equations([rec], tmp_dir)
        assert result.errors == [], f"unexpected errors: {result.errors}"
        assert len(result.files_written) == 1
        out_text = Path(result.files_written[0]).read_text()
        # Module must carry both fields
        assert "# content-hash: " in out_text
        assert SHA256_A in out_text  # source_doc_key value present
        assert "source_doc_key" in out_text

    def test_fails_closed_when_doc_key_missing(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.equations import (
            promote_equations,
        )
        rec = _eq_record(doc_key=None)
        result = promote_equations([rec], tmp_dir)
        assert result.errors
        assert result.files_written == []

    def test_fails_closed_on_malformed_doc_key(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.equations import (
            promote_equations,
        )
        rec = _eq_record(doc_key="not-a-doc-key")
        result = promote_equations([rec], tmp_dir)
        assert result.errors
        assert result.files_written == []

    def test_multiple_distinct_doc_keys_all_emitted(self, tmp_dir):
        """When a grouped module aggregates equations from multiple source
        docs, every distinct source_doc_key must appear in the header."""
        from scripts.data.doc_intelligence.promoters.equations import (
            promote_equations,
        )
        recs = [
            _eq_record(
                text=(
                    "Hydrostatic pressure: P = rho * g * d, where rho is "
                    "fluid density [kg/m³], g is gravitational acceleration "
                    "[m/s²], d is depth [m]. Returns pressure in Pa."
                ),
                doc_key=SHA256_A,
            ),
            _eq_record(
                text=(
                    "Buoyancy force: F_b = rho * g * V, where rho is fluid "
                    "density [kg/m³], g is gravitational acceleration "
                    "[m/s²], V is displaced volume [m³]. Returns force in N."
                ),
                doc_key=SHA256_B,
            ),
        ]
        result = promote_equations(recs, tmp_dir)
        assert result.errors == [], f"unexpected errors: {result.errors}"
        out_text = Path(result.files_written[0]).read_text()
        assert SHA256_A in out_text
        assert SHA256_B in out_text
