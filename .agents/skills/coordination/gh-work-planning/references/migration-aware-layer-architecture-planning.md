# Migration-aware layer architecture planning

Use this reference when planning data/execution/report architecture issues in a repo ecosystem where current paths reflect partial migrations rather than clean ownership.

## Trigger

The user clarifies that data or artifacts were moved piecemeal, or resource intelligence shows overlapping raw data, private wiki, public wiki, execution outputs, reports, archives, scratch folders, or legacy aliases.

## Planning rule

Do not treat the current filesystem layout as the intended architecture. First classify residency and ownership, then plan boundaries.

Recommended issue structure:
1. Keep the broad data/execution/report issue as an umbrella or cross-layer lifecycle contract.
2. Split data, execution, and report concerns into child issues if they have separate approval surfaces.
3. Make data inventory/normalization a dependency before approving irreversible data-layer boundary decisions.
4. Let execution/report plans proceed only interface-first while data residency is unresolved.
5. Avoid creating a duplicate umbrella if a parent/child issue tree already exists; comment on the existing parent with the recommendation and sequencing.

## Data inventory classes to require

At minimum, classify each candidate path/source as one of:
- canonical raw/private source
- readable raw derivative
- private llm-wiki / private corpus
- public llm-wiki eligible derivative
- generated evidence/output
- client-facing report surface
- scratch / temporary / run artifact
- archive / legacy alias / moved-but-not-normalized residue
- unknown / fail-closed

## Contract fields for dependent execution/report layers

While inventory is incomplete, dependent plans should reference data through contracts, not hardcoded paths. Prefer fields like:
- `source_id`
- `source_registry_kind`
- `registry_ref`
- `input_residency`
- `output_residency`
- evidence bundle ID/path
- promotion/publication eligibility

## Fail-closed rule

If a source or output cannot be classified, it is not eligible for:
- public llm-wiki promotion
- client-facing report publication
- chatbot ingestion
- durable canonicalization

## GitHub progress comment shape

When the user corrects the migration state mid-planning, post a concise parent-issue comment:

- Correction: current layout is migration/piecemeal state, not greenfield.
- Recommendation: reuse existing issue tree; do not create duplicate umbrella.
- Dependencies: name the inventory/taxonomy issues blocking data-boundary approval.
- Provisional interfaces: execution/report may proceed only through explicit contracts.
- Fail-closed: ambiguous sources stay private/unpublished until classified.

## Pitfalls

- Treating sibling clones, nested paths, or `/mnt` layout as canonical without evidence.
- Approving data-layer boundaries before inventory/taxonomy issues produce evidence.
- Letting execution/report issues hardcode temporary current data paths.
- Moving or deleting generated evidence/artifact roots before classifying consumers.
- Burying the sequencing correction in local notes instead of posting it to the parent issue.
