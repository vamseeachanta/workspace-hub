### Plan Review — Verdict: REQUEST_CHANGES
- P1: Dual rendering paths (MD+HTML) will drift → By design: both render from same validated data dict
- P1: CSS reuse is copy-paste → FW: create shared warm-parchment module
- P2: Schema and validator can drift → Schema is documentation; Python is source of truth
- P2: CDN-only assets → FW (consistent with all reviewers)
- P2: No adoption path for digitalmodel/assetutilities → FW: CLI contract
- P3: String tests don't verify browser rendering → Out of scope for v1

### Implementation Review — Verdict: REQUEST_CHANGES
- P1: CDN dependency → FW: --self-contained flag
- P1: XSS in chart scripts → MITIGATED: all chart data serialized via json.dumps(), not string interpolation; data table cells now html_escaped (fixed)
- P2: Weak validation → Accepted for v1; field presence + type enum checks sufficient
- P2: Dual renderer drift → By design; both from same data dict
- P3: Equation numbering stability → IDs from YAML are stable
- P3: CDN version pinning → Versions ARE pinned (KaTeX 0.16.11, Chart.js 4.4.6); SRI hashes FW
