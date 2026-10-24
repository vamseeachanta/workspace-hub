# Presence comparison state

`api-catalog-snapshot.json` starts with an empty public projection. This seed
avoids inventing a historic successful review or carrying stale capability counts.
It is intentionally uninitialized; the first comparison requires a full review.

Keep operational copies and review receipts in approved private storage. Only
public-safe state may be proposed back to this repository. Private/internal rows
are represented only by `private_internal_count`. No descriptions, scopes,
absolute source paths or raw receipt fields are persisted.

The procedure and worked example are in
`scripts/marketing/deckhand-api-presence-sync/SKILL.md`. Advance a snapshot only
after all surface proposals have open draft PRs and the matching receipt passes.
No-op runs need no advancement. Serialize updates and preserve previous evidence
until the state change is reviewed. A local receipt cannot authenticate remote PRs.
