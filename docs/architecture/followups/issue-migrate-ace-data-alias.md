# Migrate `/mnt/ace-data` alias references

## Scope
Inventory durable references to the `/mnt/ace-data` compatibility alias, classify each reference as operational, archival, or stale, and migrate active references to canonical `/mnt/ace` path-family language or neutral placeholders.

## Non-goals
- Do not delete the symlink in this issue.
- Do not expose private/client root paths in public docs.

## Acceptance criteria
- Active durable references no longer require `/mnt/ace-data`.
- Archival references are either justified or moved to an internal/private artifact.
- A separate cleanup decision records whether symlink deletion is safe.
- Work remains plan-gated before implementation.
