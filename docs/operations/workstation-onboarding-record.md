# Reading the workstation onboarding record

The registry records completed equivalence onboarding for the GPU executor.
Installed tooling includes `uv`; the notes record the completed checkout,
managed cron and confirmed sentinel publication. This is historical evidence,
not a measurement of current readiness.

## Revision history

| Revision | Date | Change and reason |
| --- | --- | --- |
| Initial | 2026-10-22 | Explain the corrected onboarding record and provide a reproducible example to prevent stale pending claims. |

## Evidence and method

The completion comment in #3507, dated 2026-07-23, records the checkout,
installed `uv`, managed cron and successful publication. The confirmation
comment in #3594, dated 2026-07-29, identifies the stale registry fields and
separates remaining readiness findings from completed onboarding. These are
the sources for the expected facts in the regression tests. No engineering
equations, coefficients or acceptance limits are used.

The tools and notes are corrected in `config/workstations/registry.yaml`.
The workspace path, sibling layout and `contribute-minimal` schedule remain
unchanged. A separate comment immediately above the workspace path supersedes
the historical inline pending note; the existing path line is preserved
verbatim to avoid republishing a restricted locator.

## Worked example

Input: the repository's workstation registry. Select the record by its existing
`gpu-executor` role, check that its tool list contains `uv`, then compare its
notes with the independently transcribed completion facts. The expected answer
is that all facts are present and the schedule remains `contribute-minimal`.
Run from the repository root in a Python environment with PyYAML available:

```python
from pathlib import Path

import yaml

registry = yaml.safe_load(Path("config/workstations/registry.yaml").read_text())
records = [
    record
    for record in registry["machines"].values()
    if record["role"] == "gpu-executor"
]
(record,) = records

# Expected facts: #3507 completion comment, 2026-07-23.
expected = (
    "workspace-hub clone complete",
    "uv installed",
    "managed cron active",
    "machine-keyed sentinel publication confirmed",
)
assert "uv" in record["capabilities"]["tools"]
assert all(fact in record["notes"].lower() for fact in expected)
assert record["schedule_variant"] == "contribute-minimal"
print("Recorded onboarding complete; current readiness requires fresh evidence.")
```

Expected output:

```text
Recorded onboarding complete; current readiness requires fresh evidence.
```

The same facts are exercised by `TestCompletedOnboarding` in
`tests/workstations/test_registry.py`, alongside a check that the checkout
remains a sibling under the recorded repository root.

## Limits and follow-up

This correction does not inspect a remote installation, change scheduled jobs
or mark unrelated readiness findings resolved. Identity-file enrollment raised
in the confirmation comment remains separate from this registry correction.
Before changing a live schedule or readiness verdict, obtain fresh evidence
for that operation. The historical completion record alone is insufficient.
