### Plan Review — Verdict: REQUEST_CHANGES
- P2: CDN-only KaTeX/Chart.js (no offline fallback) → FW
- P2: File naming snake_case vs kebab-case → justified exception (Python imports)
- P2: Test file >400 lines → Fixed (conftest.py extraction)
- P2: Markdown intermediate unclear value → MD is first-class deliverable
- P2: No LaTeX/chart validation → throwOnError:false; FW for server-side

### Implementation Review — Verdict: APPROVE
- P3: Data table cells not html_escaped → Fixed
- P3: Numeric values not escaped → defense-in-depth; values are numeric
- P3: File naming inconsistency → justified exception
- P3: chart ID escape inconsistency → IDs are alphanumeric by schema
- P3: Pipe chars in MD table → edge case; FW
- P3: Schema is descriptive, not machine-enforceable → accepted
