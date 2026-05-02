# Elements dedupe-merge next-phase checklist

Issue: https://github.com/vamseeachanta/workspace-hub/issues/2526

Staged copy is complete and verified. This checklist is for the next phase only. Do not perform these merges without explicit approval for each bucket or approved batch.

## Global pre-merge rules

1. Keep `/mnt/elements` retained for at least 30 days after final destination verification.
2. Do not delete `_from_elements/` staging folders until after parent merge is verified and retained backups/manifests are confirmed.
3. For each bucket, run duplicate/overlap assessment before moving files.
4. Use dry-run first for every merge command.
5. Preserve conflicting versions by renaming or quarantining; do not overwrite silently.
6. Update the relevant `MOVE-LOG.md` after each merge.

## Bucket order recommendation

Start with smallest/lowest-risk buckets, then large/overlapping buckets:

1. `digitalmodel-suction-pile-sizing` — 4 files / 235,464 bytes
2. `assethold-casa-grande-77017` — 3 files / 16,703,705 bytes
3. `digitalmodel-qgis` — 3 files / 398,492,107 bytes
4. `digitalmodel-riser-toolbox` — 8 files / 510,241,677 bytes
5. `doris-62092-sesa` — 418 files / 1,465,267,463 bytes; likely overlap
6. `doris-university` — 564 files / 11,060,962,662 bytes
7. `doris-codes-specs` — 35,197 files / 26,411,658,490 bytes; high file-count overlap risk
8. `acma-projects-31522-woodfibre` — 5,364 files / 1,879,405,139,855 bytes; very large, treat as separate reviewed merge

## Per-bucket assessment pattern

For bucket with parent `PARENT` and staging `STAGE`:

```bash
# 1. Inventory parent and stage
find "$PARENT" -path "$STAGE" -prune -o -type f -printf '%P\t%s\n' | sort > parent-files.tsv
find "$STAGE" -type f -printf '%P\t%s\n' | sort > stage-files.tsv

# 2. Compare same relative path + same size vs conflicts
join -t $'\t' -a1 -a2 -e '' -o '0,1.2,2.2' parent-files.tsv stage-files.tsv > joined.tsv
awk -F '\t' '$2 != "" && $3 != "" && $2 == $3 {print}' joined.tsv > exact-path-size-overlap.tsv
awk -F '\t' '$2 != "" && $3 != "" && $2 != $3 {print}' joined.tsv > path-size-conflicts.tsv
awk -F '\t' '$2 == "" && $3 != "" {print}' joined.tsv > new-from-stage.tsv

# 3. Review counts before merge
wc -l parent-files.tsv stage-files.tsv exact-path-size-overlap.tsv path-size-conflicts.tsv new-from-stage.tsv
```

## Merge approach after assessment

- If only new files: dry-run `rsync -aHAXn --ignore-existing "$STAGE/" "$PARENT/"`, then run without `-n`.
- If exact path+size overlaps exist: keep parent copy; do not overwrite; use `--ignore-existing`.
- If path-size conflicts exist: do not merge those paths automatically. Move conflicts into a reviewed conflict folder or decide case-by-case.
- After merge, rerun parent-vs-stage inventory and document what remains only in stage.

## Codes & Regulations

Still skipped. Before any ingest, compare source against `/mnt/ace/acma-codes/` with inventory/checksum sampling and create a separate decision note.
