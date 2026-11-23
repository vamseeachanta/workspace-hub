# GTM cross-review readiness — 2026-04-15 (updated)

## Scope reviewed
- Issue tracker and recent GTM work: #2016, #1809, #2288, #2116, #2118, #2087, #2030, #2035, #2090, #2095, #2098, #1669, #191, #117
- Recent commits and artifacts in:
  - `digitalmodel/examples/demos/gtm/*`
  - `aceengineer-website/content/demos/*`
  - `aceengineer-website/content/methodology/*`
- GTM collateral under `docs/gtm/*`
- Local built-site verification via `http://127.0.0.1:8788/*`
- Production spot checks for currently live aceengineer.com URLs

## Executive summary
The GTM stream is materially closer to approval now.

Cleanup completed in this pass:
1. Removed the stale `Texas #XXXXX` credential placeholder from GTM collateral
2. Repaired the demo gallery's broken Demo 5 detailed-report path by adding `jumper-installation.html` into both source and built-site outputs
3. Implemented the 4 methodology pages in the website source/build tree and linked them from the demo gallery methodology section

Current approval posture:
- demo/engineering core: ready
- local website/collateral artifacts: ready for user review
- production deployment state: not fully verified/live yet
- issue tracker/body hygiene: still needs reconciliation

## What was fixed
### 1) Capability summary placeholder removed
Files fixed:
- `docs/gtm/capability-summary.md`
- `docs/gtm/website-pages/capability-summary.html`

Replacement:
- `Licensed P.E. --- Houston, TX`
- `Licensed P.E. &mdash; Houston, TX`

Verification:
- repo search for `Texas #XXXXX` under `docs/gtm` now returns no matches

### 2) Demo gallery broken link fixed
Files added:
- `aceengineer-website/content/demos/jumper-installation.html`
- `aceengineer-website/dist/demos/jumper-installation.html`

Verification:
- `http://127.0.0.1:8788/demos/jumper-installation.html` -> `200`
- browser validation succeeded on the detailed report page

### 3) Methodology pages implemented and linked from gallery
Files added:
- `aceengineer-website/content/methodology/compound-engineering/index.html`
- `aceengineer-website/content/methodology/enforcement/index.html`
- `aceengineer-website/content/methodology/orchestrator-worker/index.html`
- `aceengineer-website/content/methodology/multi-agent-parity/index.html`
- `aceengineer-website/dist/methodology/compound-engineering/index.html`
- `aceengineer-website/dist/methodology/enforcement/index.html`
- `aceengineer-website/dist/methodology/orchestrator-worker/index.html`
- `aceengineer-website/dist/methodology/multi-agent-parity/index.html`

Gallery links added in:
- `aceengineer-website/content/demos/index.html`
- `aceengineer-website/dist/demos/index.html`

Local verification:
- `http://127.0.0.1:8788/methodology/compound-engineering/` -> `200`
- `http://127.0.0.1:8788/methodology/enforcement/` -> `200`
- `http://127.0.0.1:8788/methodology/orchestrator-worker/` -> `200`
- `http://127.0.0.1:8788/methodology/multi-agent-parity/` -> `200`
- browser validation succeeded on methodology pages and demo gallery links

## Remaining blockers / caveats
### A. Production deployment not yet confirmed
Production spot checks still show:
- `https://aceengineer.com/demos/` -> `200`
- `https://aceengineer.com/methodology/compound-engineering` -> `404`
- `https://aceengineer.com/methodology/enforcement` -> `404`
- `https://aceengineer.com/methodology/orchestrator-worker` -> `404`
- `https://aceengineer.com/methodology/multi-agent-parity` -> `404`

Interpretation:
- local implementation is now present and reviewable
- production deployment is still pending or not yet propagated

### B. GTM tracker / issue hygiene still stale
Still needs reconciliation before final approval package is truly clean:
- `#2016` tracker body is stale vs shipped work
- `#1669` still reflects old blockers/file paths
- `#117` stale paths/status vs actual artifacts
- `#191` stale scope/status vs current artifact reality
- `#2098` could use minor closure reconciliation

## Updated approval matrix
### Ready for user review now
- `#2087` ready
- `#2118` ready
- `#1809` ready
- `#2288` ready
- `#2090` ready after placeholder cleanup
- `#2116` ready for local artifact review after detailed-report fix + methodology links
- `#2030` ready for local artifact review, but not yet production-live
- `#2095` ready with caution

### Still needs reconciliation before final approval signoff
- `#2016`
- `#1669`
- `#117`
- `#191`
- `#2098` minor cleanup

### Approve only with scoped note
- `#2035` if scoped to the evidenced catenary/manim deliverable only

## Recommended next actions
1. Review the updated local website artifacts for `#2116` and `#2030`
2. If approved, deploy/publish the methodology pages so production 404s disappear
3. Reconcile `#2016` tracker state against shipped GTM work
4. Clean up stale issue bodies for `#1669`, `#117`, and `#191`

## User-review recommendation
You can now review the GTM work in two layers:

1. **Approve the implemented artifact layer**
   - demos
   - GIFs
   - gallery page
   - methodology page implementations

2. **Hold final GTM signoff on two remaining admin items**
   - production deployment confirmation
   - issue/tracker hygiene reconciliation
