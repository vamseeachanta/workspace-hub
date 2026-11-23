"""Synthetic worked example for issue 3851 (2026).

Run from the repository root: python -m examples.governance.recorded_evidence
The expected pass/pass/fail answers follow literal byte inspection; no numerical
engineering criterion or solver is involved. See the recorded-evidence contract.
"""
from __future__ import annotations

import json

from scripts.governance.evidence_classification import assess_content


def run_example() -> dict:
    """Compare two labels on identical bytes, then change the checked content."""
    payload = b"result=synthetic\n"
    checks = {
        "record": lambda data: data.startswith(b"result="),
        "newline": lambda data: data.endswith(b"\n"),
    }
    return {
        "reproduction": assess_content(payload, recorded_class="format_reproduction", checks=checks),
        "relabeled": assess_content(payload, recorded_class="native_capture", checks=checks),
        "changed_content": assess_content(
            b"result=synthetic", recorded_class="native_capture", checks=checks),
    }


if __name__ == "__main__":
    print(json.dumps(run_example(), indent=2, sort_keys=True))
