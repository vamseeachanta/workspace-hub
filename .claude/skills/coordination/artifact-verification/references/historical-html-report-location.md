# Historical HTML Report Location Pattern

Use this when the user asks for the location of a generated HTML/report artifact from prior work and the local checkout may not contain the sibling repo.

## Pattern

1. Search session history for distinctive terms from the user's phrasing plus likely corrected spellings. Example: `sorroco` → `sirocco`.
2. Extract the artifact path, owning issue, and generation context from the prior session.
3. If the expected local repo path is missing, do not keep retrying the same path. Inventory live repo roots, then switch to remote verification.
4. Verify the artifact exists in the canonical GitHub repo via Contents/API metadata. Capture at least:
   - repo
   - issue URL/title/status if available
   - artifact path
   - raw/download URL
   - size
   - SHA
5. Tell the user whether the artifact is remote-only vs locally present. If local checkout is absent, state that follow-up edits require clone/sync first.

## Example shape

```text
Repo: vamseeachanta/digitalmodel
Issue: #598 — feat(naval-architecture): SIROCCO current-heading/rudder force component chart set
Artifact: outputs/b1528_sirocco/current_heading_rudder_30deg_limit/b1528_sirocco_current_heading_rudder_30deg_limit_report.html
Raw URL: https://raw.githubusercontent.com/.../report.html
Verified: size=<bytes>, sha=<sha>
Local state: /mnt/local-analysis/digitalmodel absent; clone/sync required before edits.
```

## Pitfall

A session-history path can be true historically but not present on the current machine. Always distinguish historical path evidence, remote GitHub evidence, and live local filesystem evidence.
