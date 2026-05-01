# #2569 Implementation Review — B1528 SIROCCO source pack

Verdict: APPROVE

Reviewer: Hermes follow-up adversarial review after initial MAJOR findings.

## Scope reviewed

- `docs/projects/acma/B1528/sirocco-rudder-source-pack.md`
- `docs/projects/acma/B1528/sirocco-turning-benchmark.yaml`
- `scripts/validation/validate_b1528_source_pack.py`
- `knowledge/wikis/acma-projects/wiki/concepts/b1528-sirocco-rudder-yaw-moment-inputs.md`

## Prior findings and disposition

1. **Ft/Fn formula ambiguity** — resolved. Source pack distinguishes evaluated workbook formulas (`Ft = F sin(alpha) cos(alpha)`, `Fn = F sin(alpha)`) and documents that the evaluated yaw-moment cell uses `Fn` via `C23`, while workbook text says `Ft * LBP * 0.60`.
2. **Incomplete VDR extraction / source-line traceability** — resolved. Benchmark YAML contains 84 VDR points and 21 Rosepoint points, with `source_paragraph_index` and explicit `source_line_basis` on extracted points.
3. **Weak validator** — resolved. Validator checks key text, narrative benchmark classification, VDR/Rosepoint counts, sentinel timestamps, first parsed point, and source-line basis.
4. **Weak 0.935 citation** — resolved. Wiki now cites starboard prop-rotation factor to the Barrass sheet note and treats converted script as corroborating only.

## Verification commands

```bash
UV_NO_SYNC=1 uv run --with openpyxl --with python-docx --with pyyaml /tmp/generate_b1528_source_pack.py
UV_NO_SYNC=1 uv run --with pyyaml scripts/validation/validate_b1528_source_pack.py
UV_NO_SYNC=1 uv run scripts/knowledge/llm_wiki.py lint --wiki acma-projects
```

All passed.

## Required fixes

None.
