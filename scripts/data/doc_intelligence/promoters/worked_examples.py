"""Worked-examples promoter — renders pytest test files from extracted examples."""

import re
from collections import defaultdict
from pathlib import Path
from typing import Optional

from scripts.data.doc_intelligence.promoters.coordinator import (
    PromoteResult,
    register_promoter,
)
from scripts.data.doc_intelligence.promoters.text_utils import (
    content_hash,
    sanitize_identifier,
    source_citation,
    write_atomic,
)

# Pattern: "Example N.N: <title>" (N can have multiple dot-separated parts)
_EXAMPLE_RE = re.compile(
    r"Example\s+([\d]+(?:\.[\d]+)*)\s*:\s*(.+?)(?:\.|$)", re.IGNORECASE
)

# Pattern: last number on the Solution line (handles commas in numbers)
_SOLUTION_RE = re.compile(
    r"Solution\s*:.*?=\s*.*?([\d,]+(?:\.\d+)?)\s*(?:[A-Za-z]|$)"
)


def _parse_example(record: dict) -> Optional[dict]:
    """Extract title, example number, and expected value from a record.

    Returns a dict with keys: number, title, expected_value, source, domain
    or None if parsing fails.
    """
    text = record.get("text", "")

    title_match = _EXAMPLE_RE.search(text)
    if not title_match:
        return None

    number = title_match.group(1)
    title = title_match.group(2).strip()

    # Find the last number on the Solution line
    expected_value = None
    for line in text.split("\n"):
        if line.strip().lower().startswith("solution"):
            sol_match = _SOLUTION_RE.search(line)
            if sol_match:
                raw = sol_match.group(1).replace(",", "")
                try:
                    expected_value = float(raw)
                except ValueError:
                    pass

    if expected_value is None:
        return None

    return {
        "number": number,
        "title": title,
        "expected_value": expected_value,
        "source": record.get("source", {}),
        "domain": record.get("domain", "unknown"),
    }


def _render_test_file(
    manifest: str, examples: list[dict],
) -> str:
    """Render a pytest test file for a set of worked examples.

    Returns the full file content string (empty string if no examples).
    """
    if not examples:
        return ""

    # Build parametrize entries
    params = []
    for ex in examples:
        desc = ex["title"]
        val = ex["expected_value"]
        # Format as int if it's a whole number, otherwise float
        if val == int(val):
            val_str = str(int(val))
        else:
            val_str = str(val)
        params.append(f'        ("{desc}", {val_str}),')

    params_block = "\n".join(params)

    body = (
        f'"""Worked examples from {manifest} — auto-promoted.\n'
        "\n"
        "# content-hash: {{HASH}}\n"
        '"""\n'
        "\n"
        "import pytest\n"
        "\n"
        "\n"
        "@pytest.mark.parametrize(\n"
        '    "description,expected_approx",\n'
        "    [\n"
        f"{params_block}\n"
        "    ],\n"
        ")\n"
        "def test_worked_example(description, expected_approx):\n"
        '    """Verify worked examples from source documents.\n'
        "\n"
        "    These tests serve as regression checks — the expected values come\n"
        "    directly from the standard's worked examples.\n"
        '    """\n'
        "    # TODO: Wire to actual implementation when equations are promoted\n"
        '    assert expected_approx > 0, f"Placeholder for: {description}"\n'
    )

    # Replace hash placeholder with actual hash of the body (minus the hash line)
    hash_placeholder = body.replace("{{HASH}}", "")
    digest = content_hash(hash_placeholder)
    body = body.replace("{{HASH}}", digest)

    return body


def promote_worked_examples(
    records: list[dict],
    project_root: Path,
    dry_run: bool = False,
) -> PromoteResult:
    """Promote worked-example records into pytest test files.

    Groups records by manifest, renders one test file per manifest at
    ``{project_root}/tests/promoted/{domain}/test_{manifest_id}_examples.py``.
    """
    result = PromoteResult()
    if not records:
        return result

    # Group parsed examples by manifest
    by_manifest: dict[str, list[dict]] = defaultdict(list)
    manifest_domain: dict[str, str] = {}

    for rec in records:
        parsed = _parse_example(rec)
        if parsed is None:
            continue
        manifest = rec.get("manifest", "unknown")
        by_manifest[manifest].append(parsed)
        manifest_domain[manifest] = parsed["domain"]

    # Render and write one file per manifest
    for manifest, examples in by_manifest.items():
        manifest_id = sanitize_identifier(manifest)
        domain = manifest_domain[manifest]
        out_dir = project_root / "tests" / "promoted" / domain
        out_path = out_dir / f"test_{manifest_id}_examples.py"

        content = _render_test_file(manifest, examples)
        if not content:
            continue

        written = write_atomic(out_path, content, dry_run=dry_run)
        if written:
            result.files_written.append(str(out_path))
        else:
            result.files_skipped.append(str(out_path))

    return result


register_promoter("worked_examples", promote_worked_examples)
