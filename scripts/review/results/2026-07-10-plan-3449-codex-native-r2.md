# Adversarial plan review — #3449 (native Codex, r2)

Plan: `docs/plans/2026-07-10-issue-3449-client-wiki-metadata-only-bootstrap.md`
Reviewed commit: `acaf48aa3197b76f2cbc96467dc32b3a3f19f32a`
Reviewed: 2026-07-10

## Verdict

MAJOR

## Retrieval

- Read the pushed plan at the reviewed commit.
- Compared its renderer preconditions with `.claude/skills/coordination/client-llm-wiki-factory/SKILL.md`.
- Compared its proposed authority fields with the aggregate field shape of the provisioned private registry; no private values were retained.
- Rechecked the existing registry checker's optional `local_working_clone` behavior.

## Findings

1. **The destination/root authority contract is undefined.** The plan relies on `raw_root_bases` and `working_clone_base` at plan lines 183 and 189–190 without defining them as schema fields, CLI inputs, environment inputs, or derived values. Neither field exists in the authoritative registry shape. The current checker treats `local_working_clone` as optional, and the factory adds that field only after bootstrap. Implementation would have to invent security-critical trust roots and destination semantics.

2. **The renderer cannot fit the factory's Git lifecycle.** The factory creates the remote, clones it locally, then copies the template into that existing clone before committing and pushing. The plan instead requires an absent destination and creates it itself. Running the renderer after clone would reject the destination; running it before clone would leave no `.git` and prevent the documented clone. The documentation-order test does not exercise this end-to-end boundary.

3. **The no-overwrite/cleanup guarantee remains underspecified.** Recording a destination inode and using exclusive child creation does not define directory-fd-relative traversal, no-follow behavior, or race-safe cleanup, while the plan claims racing sentinels remain unchanged and only owned content is removed. Once rendering targets an existing clone, cleanup must never remove the clone or `.git`.

## Blockers

- Define destination derivation entirely from existing trusted inputs; do not invent absent registry fields.
- Make the renderer operate on a verified empty clone whose origin matches the registered private repository.
- Specify directory-fd-anchored, no-follow, exclusive writes plus a created-artifact ledger; cleanup must be limited to recorded template artifacts and must preserve the clone and `.git`.

## Residual risks

- The original r1 MAJORs were materially resolved: the raw-read/FFI scope was removed, implementation was split, and checker invocation/exit behavior was specified.
- Schema `0.2` deliberately rejects every enabled-ingestion state and makes no ecosystem-wide reader-enforcement claim; that boundary must remain.
- The plan cannot enter `status:plan-review` with these findings unresolved.
