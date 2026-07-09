---
name: achantas-data-repo-personal-family-data
description: "vamseeachanta/achantas-data (PRIVATE) holds family PII + docs, organized by per-person prefix; travel plans tracked as GitHub issues"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 1b0830df-075b-47ac-a7f8-a686fe23b1d1
---

**Repo:** `vamseeachanta/achantas-data` (GitHub, **PRIVATE** — `isPrivate: true`, verified 2026-07-06)
**Local clone:** `/mnt/local-analysis/achantas-data` (sibling of workspace-hub, its own git repo — `cd` in before git ops)

Personal/family data-management repo. It **intentionally stores sensitive PII as tracked files** — SSNs, passports, passport cards, green cards, Aadhaar cards, birth certificates, medical/lab reports, driver's licenses. This is safe *only because the repo is private*; always verify `gh repo view --json isPrivate` before committing PII, and never push family documents to any public remote.

**Per-person folder + filename convention** (match it when filing new docs):
- `da/` = Devakrishna (child) — his identity docs use a `DA_` prefix (`DA_Passport.pdf`, `DA_OCI.pdf`, `DA_SSN.jpg`, `Krishna_BirthCertificate_Only.pdf`)
- `sd/` = Sabitha — e.g. `sd/Sabitha_SSN.pdf`, `sd/ID/`
- `va/` = Vamsee — e.g. `va/VA_SSN.pdf`, `va/VA Aadhaar Card.pdf`
- SSN files use a `_SSN` suffix; store new identity scans next to the person's existing passport/birth-certificate.
- Other top-level areas: `_health/`, `_house/`, `_will/`, `_travel/`, `_finance/`, `_relations/`, `corpus/`.

2026-07-06: added `da/DA_SSN.jpg` (Devakrishna's Social Security card scan) via PR #149 — the repo previously had both parents' SSNs but not the child's.

**Filing gotcha:** this repo runs an auto-sync daemon, so local `main` can diverge from origin (local-only merge artifacts + duplicate commits). Before `reset --hard origin/main`, diff the local-only commits' content against origin to confirm they're duplicates — they usually are. See [[feedback_equality_wedge_vs_drift_recovery]]. For new personal plans/logistics, default to GitHub issues (`gh issue create --repo vamseeachanta/achantas-data`).
