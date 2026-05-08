# Offshore Intervention / HSE / Riser Automation Outreach Pattern

Use when a prospect conversation is about offshore intervention, abandonment, decommissioning, HSE inputs, riser analysis, or integrated public-data + engineering automation rather than a single vessel-suitability demo.

## Trigger

- User names a prospect/contact and asks to prepare outreach around intervention/abandonment, HSE, riser analysis, OrcaFlex, worldenergydata, or digitalmodel automation.
- The ask is GTM/outreach planning, not immediate email sending.

## Reusable Workflow

1. **Keep prospect PII out of Git**
   - Public profile URLs supplied by the user may be referenced.
   - User-supplied public profile role history may be captured as planning context when it materially changes positioning; label it as user-supplied and recheck immediately before send if using role-specific language.
   - Do not store private email, phone, CRM export rows, or scraped contact details in repo files.
   - If LinkedIn is authwalled and the user has not supplied role context, record that role/company was not verified and avoid personalization claims.

2. **Ground capability across repos before writing copy**
   - In `worldenergydata`, inspect readiness for public intervention/abandonment, wellbore, marine-safety, HSE, incident, and safety-analysis inputs.
   - In `digitalmodel`, inspect readiness for riser/OrcaFlex automation, riser configuration utilities, report renderers, and related issue anchors.
   - In strategy repo, search for existing prospect or segment entries to avoid duplicate planning artifacts.

3. **Prepare a strategy-side plan artifact**
   - Use a PII-safe filename under `aceengineer-strategy/pipeline/proposals/`.
   - Include objective, current-role verification caveat, repo-grounded readiness signals, known gaps, required collateral, draft email, LinkedIn short note, call agenda, caveats, and next actions.
   - Update `pipeline/prospects.md` with a concise, non-private prospect/segment entry.

4. **Create a tracking issue**
   - Use `aceengineer-strategy` for outreach planning issues.
   - Search existing issues first.
   - Labels commonly used for this planning stage: `strategy`, `status:scoping`, `priority:P1`.
   - Issue body should state that no email is sent until user approves final email and attachments.

5. **Define the minimum credible packet before sending**
   - `worldenergydata` one-pager: intervention / abandonment public-data readiness.
   - `worldenergydata` one-pager: offshore HSE incident/risk input matrix.
   - `digitalmodel` one-pager or sample: riser / OrcaFlex automation.
   - Optional vessel-suitability PDF/sample only if the role overlaps installation, IMR, decommissioning, or vessel operations.

## Claim Discipline

- Separate production-ready, sample-only, and roadmap capabilities.
- Brochure/external-market references are positioning inputs, not design-basis evidence.
- Frame as a low-risk technical exchange or proof-of-value packet, not generic AI automation.
- Use concrete asks: 20–30 minute technical call, review of one case/vessel/scope, or permission to send a sample packet.

## Known Useful Anchors

`worldenergydata` readiness signals from the 2026-05-07 Scott Sanantonio planning session:

- `src/worldenergydata/cli/commands/marine_safety.py` — marine-safety CLI with sources like USCG/NTSB/BSEE/MAIB/TSB and export modes.
- `src/worldenergydata/safety_analysis/adapters/hse_adapter.py` — HSE incident/observation normalization adapter.

`digitalmodel` readiness signals:

- `src/digitalmodel/orcaflex/riser_config.py` — analytical riser configuration utilities for SCR/lazy-wave/TTR/weight-in-water.
- `src/digitalmodel/solvers/orcaflex/reporting/renderers/riser.py` — riser reporting renderer with dynamic-result insertion patterns.

Example strategy artifact from the same session:

- `aceengineer-strategy/pipeline/proposals/scott-sanantonio-offshore-data-riser-automation-outreach-plan-2026-05-07.md`
