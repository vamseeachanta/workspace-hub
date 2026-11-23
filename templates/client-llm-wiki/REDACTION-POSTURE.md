# Redaction Posture — <CLIENT_SHORT_NAME>

This file defines the default redaction posture for promoting content from this private wiki to the public `llm-wiki` repo. It does NOT govern content *inside* this private wiki, where client legal name, project IDs, and other identifiers are legitimate working context.

## Scope

| Surface | Posture |
|---|---|
| Inside this private wiki (pages, sources, ledgers, reports) | Client identifiers are LEGITIMATE working context. No redaction required. |
| Public-promotion path (private wiki → reviewed/sanitized derivative → public `llm-wiki`) | Apply the default table below. |

## Default redaction table

| Category | Default action |
|---|---|
| Client legal name | REDACT |
| Project IDs (B-numbers, job codes) | REDACT |
| Personal names | FLAG-FOR-REVIEW |
| Geographic coordinates | FLAG-FOR-REVIEW |
| Vessel names | FLAG-FOR-REVIEW |
| Financial figures | REDACT |

### Action meanings

- **REDACT** — Replace the identifier with a generic placeholder (e.g., `[CLIENT]`, `[PROJECT-ID]`, `[FIGURE]`) before any public-promotion ledger entry can be opened. The promotion ledger entry must record what was redacted and how.
- **FLAG-FOR-REVIEW** — The category is not auto-redacted, but the page cannot be promoted to public `llm-wiki` until an operator has reviewed every occurrence and either redacted it or explicitly cleared it with rationale recorded in the ledger.

## Per-client overrides

The default table is a baseline. For <CLIENT_SHORT_NAME> specifically, the operator may tighten or loosen individual categories below. Tighter (e.g., promote a FLAG to REDACT) is always allowed; looser (e.g., promote a REDACT to FLAG) requires explicit operator approval recorded here AND in the ledger.

### <CLIENT_SHORT_NAME> overrides

<!-- Document any <CLIENT_SHORT_NAME>-specific deviations from the default table here. -->
<!-- Format:                                                                          -->
<!--   - Category: <name>                                                              -->
<!--   - Default: REDACT | FLAG-FOR-REVIEW                                             -->
<!--   - Override: REDACT | FLAG-FOR-REVIEW | ALLOW                                    -->
<!--   - Rationale: <operator rationale>                                               -->
<!--   - Recorded by: <operator>                                                       -->
<!--   - Date: <YYYY-MM-DD>                                                            -->

_None recorded yet._

## Cross-reference

- `DATA-CYCLE.md` — overall 4-layer residency contract and promotion gates.
- `.claude/CLAUDE.md` — agent posture; forbids public promotion without sanitization review.
- `ledgers/promotion-ledger.example.yml` — promotion-ledger schema; each promotion records redaction decisions.
