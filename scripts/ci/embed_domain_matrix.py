"""Embed stdlib helpers into the reusable workflow at its own revision.

GitHub's Contexts reference (accessed 2026-10-22) does not document
`github.job_workflow_sha`. Embedding avoids a moving tools checkout in callers.
Source: https://docs.github.com/en/actions/reference/workflows-and-actions/contexts
"""

import argparse
from pathlib import Path

SCRIPTS = ("domain_matrix_aggregate.py", "validate_selector_output.py", "quarantine_args.py")
INDENT = "          "  # Existing workflow run-block indentation, not an acceptance limit.


def render(root: Path) -> str:
    workflow = root / ".github/workflows/domain-matrix.yml"
    text = workflow.read_text(encoding="utf-8")
    for name in SCRIPTS:
        begin = f"{INDENT}# BEGIN GENERATED: {name}\n"
        end = f"{INDENT}# END GENERATED: {name}"
        before, rest = text.split(begin)
        _, after = rest.split(end)
        source = (root / "scripts/ci" / name).read_text(encoding="utf-8")
        if "DOMAIN_MATRIX_SCRIPT" in source:
            raise ValueError("script contains the reserved heredoc delimiter")
        body = (
            'mkdir -p "$RUNNER_TEMP/domain-matrix-tools"\n'
            f'cat > "$RUNNER_TEMP/domain-matrix-tools/{name}" <<\'DOMAIN_MATRIX_SCRIPT\'\n'
            + source + "DOMAIN_MATRIX_SCRIPT\n"
        )
        text = before + begin + "".join(INDENT + line if line.strip() else "\n" for line in body.splitlines(keepends=True)) + end + after
    return text


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    path = args.root / ".github/workflows/domain-matrix.yml"
    expected = render(args.root)
    if args.check:
        if path.read_text(encoding="utf-8") != expected:
            print("Embedded domain scripts are stale; run scripts/ci/embed_domain_matrix.py")
            return 1
    else:
        path.write_text(expected, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
