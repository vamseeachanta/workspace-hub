---
name: assethold spec location
description: Where design specs and planning docs live in the vamseeachanta/assethold repo (overrides brainstorming skill default and the path documented in CLAUDE.md)
type: project
originSessionId: 4e7d6b5c-9c07-4c52-81ce-ef212c62b2ee
---
In the assethold repo (`/mnt/local-analysis/workspace-hub/assethold/`), design specs, brainstorming outputs, assessment docs, and session handoffs all live in **`docs/reports/`** with `YYYY-MM-DD-<topic>.md` naming.

**Why:** `.gitignore:389` blocks `specs/` everywhere in the tree. Both the brainstorming skill default (`docs/superpowers/specs/`) and the path documented in `CLAUDE.md` Plan Locality section (`specs/repos/<repo>/`) are gitignored. The established pattern in commit history (assessment doc, handoffs, triage docs) is `docs/reports/`.

**How to apply:** When writing a spec, design doc, brainstorming output, or planning artifact for assethold, save it under `docs/reports/`. Match the existing date-prefixed naming. Don't force-add to gitignored paths or create new convention dirs (`.agent-os/specs/` doesn't exist yet either) without confirming with the user first.
