# Resource Pack: WRK-640

## Problem Context

`WRK-624` made review validation deterministic, but Claude and Gemini still failed to deliver
usable non-interactive plan reviews through the existing wrapper scripts.

## Relevant Documents/Data

- `scripts/review/submit-to-claude.sh`
- `scripts/review/submit-to-gemini.sh`
- `scripts/review/cross-review.sh`
- `scripts/review/validate-review-output.sh`
- `scripts/review/results/*plan-claude.md`
- `scripts/review/results/*plan-gemini.md`

## Constraints

- The shared review schema must stay markdown-compatible with `validate-review-output.sh`.
- Transport hardening must not weaken invalid-output classification.
- Review commands must remain non-interactive and bounded.

## Assumptions

- Provider CLIs are installed and authenticated on `ace-linux-1`.
- Provider-specific structured output can be rendered into the canonical markdown schema locally.

## Open Questions

- Whether Gemini eventually supports a strict JSON schema flag comparable to Claude.
- Whether larger commit diffs will need content truncation or chunking in a follow-on WRK.

## Domain Notes

- Root cause is environment-sensitive: running from the full repo context is materially less reliable
  than running from an isolated temporary directory.
