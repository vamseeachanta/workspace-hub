---
title: "WRK-188 Worldenergydata Wave-1 Migration Plan"
description: "Dry-run manifest and controlled apply checklist for worldenergydata spec centralization"
version: "1.8"
module: governance
status: "draft"
progress: 0
created: "2026-02-17"
updated: "2026-02-17"
priority: "high"
tags: [spec-migration, worldenergydata, governance]
links:
  wrk: ".claude/work-queue/pending/WRK-188.md"
  parent: "specs/wrk/WRK-185/ecosystem-centralization-review.md"
---

# WRK-188 Worldenergydata Wave-1 Migration

## Scope
- In scope: `worldenergydata/**/specs/**`
- Out of scope: all other repositories

## Migration Script Contract

`migrate_specs_to_workspace.sh` behavior expected for apply mode:
1. Copy files from repo-local `specs/` trees into `specs/repos/<repo>/<original-spec-path>/`.
2. Replace original local `specs/` directory with pointer `README.md`.
3. Leave no non-README files under migrated local `specs/` trees.
4. Fail-fast if any mapped target file exists before first approved apply (no overwrite of pre-wave files).
5. Idempotent apply: once wave-1 apply is complete, a second `--apply` on the same state must be a no-op (no content diff).
6. Dry-run summary line format is fixed:
   `repo=<repo> loc=<relative-spec-dir> files=<count> target=<absolute-target-path> dry_run=true`

Path mapping example:
- Source: `worldenergydata/data/modules/vessel_hull_models/hulls/converted_gdf/specs/README.md`
- Target: `specs/repos/worldenergydata/data/modules/vessel_hull_models/hulls/converted_gdf/specs/README.md`

Pointer README template (minimum):
```markdown
# Specs Pointer

Specs are centralized in:
`specs/repos/worldenergydata/<original-spec-path>/`
```

## Prerequisites

```bash
mkdir -p reports/compliance
command -v bash find cp mv rm awk sed rg python3 sha256sum sort xargs diff git du df timeout >/dev/null
test -x scripts/operations/compliance/migrate_specs_to_workspace.sh
scripts/operations/compliance/migrate_specs_to_workspace.sh --help >/dev/null
test -x scripts/operations/compliance/check_governance.sh
test -x scripts/review/cross-review.sh
test -x scripts/review/normalize-verdicts.sh
test -z "$(git status --porcelain)"
test -z "$(git -C worldenergydata status --porcelain)"
git -C worldenergydata rev-parse --git-dir >/dev/null
test "$(git submodule status -- worldenergydata | wc -l | tr -d ' ')" = "1"
git submodule status -- worldenergydata | rg -q '^[ +-U]?[0-9a-f]{40}[[:space:]]+worldenergydata'
git rev-parse --abbrev-ref --symbolic-full-name @{u} >/dev/null
git -C worldenergydata rev-parse --abbrev-ref --symbolic-full-name @{u} >/dev/null
mkdir -p specs/repos/worldenergydata
# clean-room baseline preferred; for retry runs use rollback first
test -z "$(find worldenergydata -path '*/specs/*' -type l)"
test "$(df -Pk . | awk 'NR==2{print $4}')" -gt "$(du -sk worldenergydata | awk '{print $1*2}')"
```
Assumptions:
- Commands target GNU/Linux shell toolchain (`bash`, GNU `find`, GNU `sed`, GNU coreutils).
- Unicode normalization collision handling (NFC/NFD) is out of scope for wave-1.

## File Handling Policy

1. Symlinks under `worldenergydata/**/specs/**` are not allowed for this wave (preflight rejects).
2. Content integrity is required (`sha256sum` parity).
3. Mode/timestamp differences are non-blocking for this wave (content-first migration).
4. Hidden and binary files are in scope if they match `*/specs/*`.

## Dry-Run Commands
```bash
scripts/operations/compliance/migrate_specs_to_workspace.sh --repos worldenergydata | tee reports/compliance/wrk-188-worldenergydata-dryrun.log
find worldenergydata -type f -path '*/specs/*' -print0 | sort -z | xargs -0 sha256sum > reports/compliance/wrk-188-worldenergydata-source-checksums.txt
python3 - <<'PY'
from pathlib import Path
roots = set()
src_files = []
tgt_files = []
bad_paths = []
for p in Path("worldenergydata").rglob("*"):
    s = str(p).replace("\\", "/")
    if p.is_file() and "/specs/" in s:
        if any(ord(ch) < 32 for ch in s):
            bad_paths.append(s)
        src_files.append(s)
        tgt_files.append(s.replace("worldenergydata/", "specs/repos/worldenergydata/", 1))
        roots.add(s.split("/specs/", 1)[0] + "/specs")
Path("reports/compliance/wrk-188-worldenergydata-source-spec-roots.txt").write_text("\n".join(sorted(roots)) + "\n")
Path("reports/compliance/wrk-188-worldenergydata-approved-source-files.txt").write_text("\n".join(sorted(src_files)) + "\n")
Path("reports/compliance/wrk-188-worldenergydata-approved-target-files.txt").write_text("\n".join(sorted(tgt_files)) + "\n")
Path("reports/compliance/wrk-188-worldenergydata-invalid-paths.txt").write_text("\n".join(sorted(bad_paths)))
if bad_paths:
    raise SystemExit(1)
PY
test -s reports/compliance/wrk-188-worldenergydata-dryrun.log
test -s reports/compliance/wrk-188-worldenergydata-source-spec-roots.txt
test -s reports/compliance/wrk-188-worldenergydata-approved-source-files.txt
test -s reports/compliance/wrk-188-worldenergydata-approved-target-files.txt
test "$(wc -l < reports/compliance/wrk-188-worldenergydata-source-spec-roots.txt | tr -d ' ')" -eq "$(rg -c '^repo=worldenergydata loc=.* files=[0-9]+ target=.* dry_run=true$' reports/compliance/wrk-188-worldenergydata-dryrun.log)"
test "$(rg -c '^repo=worldenergydata loc=.* files=[0-9]+ target=.* dry_run=true$' reports/compliance/wrk-188-worldenergydata-dryrun.log)" -gt 0
test -z "$(rg -n -v '^repo=worldenergydata loc=.* files=[0-9]+ target=.* dry_run=true$|^  would-move: .+$' reports/compliance/wrk-188-worldenergydata-dryrun.log | cat)"
# pre-apply target collision gate (must be empty for wave-1 fail-fast policy)
python3 - <<'PY'
from pathlib import Path
collisions = []
collisions_fold = []
for p in Path("worldenergydata").rglob("*"):
    s = str(p).replace("\\", "/")
    if p.is_file() and "/specs/" in s:
        t = s.replace("worldenergydata/", "specs/repos/worldenergydata/", 1)
        if Path(t).exists():
            collisions.append(f"{s} -> {t}")
        # Case-insensitive collision check for cross-platform safety
        tp = Path(t)
        if not tp.exists():
            parent = tp.parent
            if parent.exists():
                name_fold = tp.name.lower()
                for sibling in parent.iterdir():
                    if sibling.name.lower() == name_fold:
                        collisions_fold.append(f"{s} -> {sibling} (case-fold)")
Path("reports/compliance/wrk-188-worldenergydata-target-collisions.txt").write_text("\n".join(collisions))
Path("reports/compliance/wrk-188-worldenergydata-target-collisions-casefold.txt").write_text("\n".join(collisions_fold))
raise SystemExit(1 if collisions or collisions_fold else 0)
PY
# duplicate target-path preflight check
python3 - <<'PY'
from pathlib import Path
targets = []
for p in Path("worldenergydata").rglob("*"):
    if p.is_file() and "/specs/" in str(p).replace("\\","/"):
        targets.append(str(p).replace("worldenergydata/", "specs/repos/worldenergydata/", 1))
seen = set()
dups = set()
seen_fold = {}
dups_fold = set()
for t in targets:
    if t in seen:
        dups.add(t)
    tf = t.lower()
    if tf in seen_fold and seen_fold[tf] != t:
        dups_fold.add(f"{seen_fold[tf]} <-> {t}")
    else:
        seen_fold[tf] = t
    seen.add(t)
Path("reports/compliance/wrk-188-worldenergydata-duplicate-targets.txt").write_text("\n".join(sorted(dups)))
Path("reports/compliance/wrk-188-worldenergydata-duplicate-targets-casefold.txt").write_text("\n".join(sorted(dups_fold)))
raise SystemExit(1 if dups or dups_fold else 0)
PY
```

Dry-run review gate (required before apply):
1. Attach `reports/compliance/wrk-188-worldenergydata-dryrun.log` to WRK-188 progress update.
2. Confirm dry-run contains summary lines matching:
   `repo=worldenergydata loc=<path> files=<n> target=<path> dry_run=true`
   and line count equals `reports/compliance/wrk-188-worldenergydata-source-spec-roots.txt`.
3. Capture approved dry-run artifact hash for traceability:
```bash
sha256sum reports/compliance/wrk-188-worldenergydata-dryrun.log > reports/compliance/wrk-188-worldenergydata-dryrun.log.sha256
sha256sum reports/compliance/wrk-188-worldenergydata-source-checksums.txt > reports/compliance/wrk-188-worldenergydata-source-checksums.txt.sha256
sha256sum reports/compliance/wrk-188-worldenergydata-approved-source-files.txt > reports/compliance/wrk-188-worldenergydata-approved-source-files.txt.sha256
find worldenergydata -type f -path '*/specs/*' | wc -l > reports/compliance/wrk-188-worldenergydata-source-count.txt
printf "HUB_HEAD=%s\nWORLDENERGYDATA_HEAD=%s\n" "$(git rev-parse HEAD)" "$(git -C worldenergydata rev-parse HEAD)" > reports/compliance/wrk-188-worldenergydata-approved-heads.env
git -C worldenergydata rev-parse HEAD > reports/compliance/wrk-188-worldenergydata-pre-apply-submodule-sha.txt
# explicit approval artifact (required before apply)
test -n "${APPROVER_ID:-}"
printf "WRK=188\nSPEC=worldenergydata-wave1-migration\nSTATUS=APPROVED\nAPPROVER=%s\nHUB_HEAD=%s\nWORLDENERGYDATA_HEAD=%s\nDRY_RUN_HASH=%s\nDATE=%s\n" \
  "$APPROVER_ID" \
  "$(git rev-parse HEAD)" \
  "$(git -C worldenergydata rev-parse HEAD)" \
  "$(cut -d' ' -f1 reports/compliance/wrk-188-worldenergydata-dryrun.log.sha256)" \
  "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  > reports/compliance/wrk-188-worldenergydata-approval.txt
```

## Apply Commands (Do Not Run Before Approval)
```bash
source reports/compliance/wrk-188-worldenergydata-approved-heads.env
test "$(git rev-parse HEAD)" = "$HUB_HEAD"
test "$(git -C worldenergydata rev-parse HEAD)" = "$WORLDENERGYDATA_HEAD"
test -z "$(git status --porcelain)"
test -z "$(git -C worldenergydata status --porcelain)"
# revalidate source manifests/checksums against approved dry-run artifacts
find worldenergydata -type f -path '*/specs/*' -print0 | sort -z | xargs -0 sha256sum > reports/compliance/wrk-188-worldenergydata-source-checksums-apply-preflight.txt
diff reports/compliance/wrk-188-worldenergydata-source-checksums.txt reports/compliance/wrk-188-worldenergydata-source-checksums-apply-preflight.txt
python3 - <<'PY'
from pathlib import Path
rows = []
for p in Path("worldenergydata").rglob("*"):
    s = str(p).replace("\\", "/")
    if p.is_file() and "/specs/" in s:
        rows.append(s)
Path("reports/compliance/wrk-188-worldenergydata-approved-source-files-apply-preflight.txt").write_text("\n".join(sorted(rows)) + "\n")
PY
diff reports/compliance/wrk-188-worldenergydata-approved-source-files.txt reports/compliance/wrk-188-worldenergydata-approved-source-files-apply-preflight.txt
# pre-apply downstream path safety gate
test -z "$(rg -n 'worldenergydata/(.*/)?specs/' . -g '!.git/**' -g '!worldenergydata/**' -g '!specs/repos/worldenergydata/**' -g '!reports/**' | cat)"
test -f reports/compliance/wrk-188-worldenergydata-approval.txt
rg -q '^STATUS=APPROVED$' reports/compliance/wrk-188-worldenergydata-approval.txt
rg -q "^APPROVER=${APPROVER_ID}$" reports/compliance/wrk-188-worldenergydata-approval.txt
rg -q "^HUB_HEAD=${HUB_HEAD}$" reports/compliance/wrk-188-worldenergydata-approval.txt
rg -q "^WORLDENERGYDATA_HEAD=${WORLDENERGYDATA_HEAD}$" reports/compliance/wrk-188-worldenergydata-approval.txt
rg -q "^DRY_RUN_HASH=$(cut -d' ' -f1 reports/compliance/wrk-188-worldenergydata-dryrun.log.sha256)$" reports/compliance/wrk-188-worldenergydata-approval.txt
# bind cross-review artifacts to current spec+heads
test -f reports/compliance/wrk-188-worldenergydata-review-bindings.env
source reports/compliance/wrk-188-worldenergydata-review-bindings.env
SPEC_SHA_NOW="$(sha256sum specs/wrk/WRK-188/worldenergydata-wave1-migration.md | awk '{print $1}')"
test "$REVIEW_SPEC_SHA" = "$SPEC_SHA_NOW"
test "$REVIEW_HUB_HEAD" = "$HUB_HEAD"
test "$REVIEW_WORLDENERGYDATA_HEAD" = "$WORLDENERGYDATA_HEAD"
test "$REVIEW_CLAUDE_SHA" = "$(sha256sum "$REVIEW_CLAUDE_FILE" | awk '{print $1}')"
test "$REVIEW_CODEX_SHA" = "$(sha256sum "$REVIEW_CODEX_FILE" | awk '{print $1}')"
test "$REVIEW_GEMINI_SHA" = "$(sha256sum "$REVIEW_GEMINI_FILE" | awk '{print $1}')"
scripts/operations/compliance/migrate_specs_to_workspace.sh --apply --repos worldenergydata
find specs/repos/worldenergydata -type f -path '*/specs/*' -print0 | sort -z | xargs -0 sha256sum > reports/compliance/wrk-188-worldenergydata-target-checksums.txt
```

## Verification
1. Pre/post count parity (pre-apply source vs post-apply centralized target):
```bash
python3 - <<'PY'
from pathlib import Path
rows = []
for p in Path("specs/repos/worldenergydata").rglob("*"):
    s = str(p).replace("\\", "/")
    if p.is_file() and "/specs/" in s:
        rows.append(s)
Path("reports/compliance/wrk-188-worldenergydata-applied-target-files.txt").write_text("\n".join(sorted(rows)) + "\n")
PY
diff reports/compliance/wrk-188-worldenergydata-approved-target-files.txt reports/compliance/wrk-188-worldenergydata-applied-target-files.txt
find specs/repos/worldenergydata -type f -path '*/specs/*' | wc -l > reports/compliance/wrk-188-worldenergydata-target-count.txt
test "$(cat reports/compliance/wrk-188-worldenergydata-source-count.txt)" -eq "$(cat reports/compliance/wrk-188-worldenergydata-target-count.txt)"
```
2. Checksum diff is empty after path-normalized comparison:
```bash
python3 - <<'PY'
from pathlib import Path
def load(path: str, drop_prefix: str):
    rows = set()
    for line in Path(path).read_text().splitlines():
        if not line.strip():
            continue
        h, p = line.split(maxsplit=1)
        norm = p.strip()
        if norm.startswith(drop_prefix):
            norm = norm[len(drop_prefix):]
        rows.add((h, norm))
    return rows
src = load("reports/compliance/wrk-188-worldenergydata-source-checksums.txt", "worldenergydata/")
dst = load("reports/compliance/wrk-188-worldenergydata-target-checksums.txt", "specs/repos/worldenergydata/")
if src != dst:
    missing = sorted(src - dst)[:10]
    extra = sorted(dst - src)[:10]
    print("checksum mismatch")
    print("missing", missing)
    print("extra", extra)
    raise SystemExit(1)
PY
```
3. `worldenergydata/**/specs/README.md` pointer exists and includes:
- heading: `# Specs Pointer`
- centralized path beginning with ``specs/repos/worldenergydata/``
```bash
while IFS= read -r d; do
  test -f "$d/README.md"
  rel="${d#worldenergydata/}"
  expected="specs/repos/worldenergydata/${rel}"
  rg -q "^# Specs Pointer$" "$d/README.md"
  rg -Fq "$expected" "$d/README.md"
done < reports/compliance/wrk-188-worldenergydata-source-spec-roots.txt
```
4. Local specs trees contain only pointer README files:
```bash
test -z "$(find worldenergydata -type f -path '*/specs/*' ! -name 'README.md')"
```
5. Multi-provider plan cross-review gate (machine-checkable):
- Claude, Codex, and Gemini plan reviews are recorded.
- No unresolved `MAJOR`.
- Claude must produce a non-`NO_OUTPUT` verdict.
- If Gemini or Codex is `NO_OUTPUT`, the other two must be `APPROVE` or `MINOR`.
```bash
ls scripts/review/results/*worldenergydata-wave1-migration.md-plan-claude.md >/dev/null
ls scripts/review/results/*worldenergydata-wave1-migration.md-plan-codex.md >/dev/null
ls scripts/review/results/*worldenergydata-wave1-migration.md-plan-gemini.md >/dev/null
F_CLAUDE="$(ls -1t scripts/review/results/*worldenergydata-wave1-migration.md-plan-claude.md | head -n1)"
F_CODEX="$(ls -1t scripts/review/results/*worldenergydata-wave1-migration.md-plan-codex.md | head -n1)"
F_GEMINI="$(ls -1t scripts/review/results/*worldenergydata-wave1-migration.md-plan-gemini.md | head -n1)"
test -n "$F_CLAUDE" && test -n "$F_CODEX" && test -n "$F_GEMINI"
V_CLAUDE="$(scripts/review/normalize-verdicts.sh "$F_CLAUDE")"
V_CODEX="$(scripts/review/normalize-verdicts.sh "$F_CODEX")"
V_GEMINI="$(scripts/review/normalize-verdicts.sh "$F_GEMINI")"
SPEC_SHA="$(sha256sum specs/wrk/WRK-188/worldenergydata-wave1-migration.md | awk '{print $1}')"
printf "REVIEW_SPEC_SHA=%s\nREVIEW_HUB_HEAD=%s\nREVIEW_WORLDENERGYDATA_HEAD=%s\nREVIEW_CLAUDE_FILE=%s\nREVIEW_CLAUDE_SHA=%s\nREVIEW_CODEX_FILE=%s\nREVIEW_CODEX_SHA=%s\nREVIEW_GEMINI_FILE=%s\nREVIEW_GEMINI_SHA=%s\n" \
  "$SPEC_SHA" \
  "$(git rev-parse HEAD)" \
  "$(git -C worldenergydata rev-parse HEAD)" \
  "$F_CLAUDE" "$(sha256sum "$F_CLAUDE" | awk '{print $1}')" \
  "$F_CODEX" "$(sha256sum "$F_CODEX" | awk '{print $1}')" \
  "$F_GEMINI" "$(sha256sum "$F_GEMINI" | awk '{print $1}')" \
  > reports/compliance/wrk-188-worldenergydata-review-bindings.env
test "$V_CLAUDE" != "NO_OUTPUT"
echo "$V_CLAUDE $V_CODEX $V_GEMINI" | rg -q 'MAJOR|ERROR' && exit 1 || true
# NO_OUTPUT fallback enforcement for non-Claude providers
if [ "$V_CODEX" = "NO_OUTPUT" ] && [ "$V_GEMINI" = "NO_OUTPUT" ]; then
  echo "$V_CLAUDE" | rg -q '^(APPROVE|MINOR)$'
elif [ "$V_CODEX" = "NO_OUTPUT" ]; then
  echo "$V_CLAUDE" | rg -q '^(APPROVE|MINOR)$'
  echo "$V_GEMINI" | rg -q '^(APPROVE|MINOR)$'
elif [ "$V_GEMINI" = "NO_OUTPUT" ]; then
  echo "$V_CLAUDE" | rg -q '^(APPROVE|MINOR)$'
  echo "$V_CODEX" | rg -q '^(APPROVE|MINOR)$'
fi
```
6. Downstream path safety checks:
```bash
test -z "$(rg -n 'worldenergydata/(.*/)?specs/' . -g '!.git/**' -g '!.claude/**' -g '!worldenergydata/**' -g '!specs/**' -g '!reports/**' | cat)"
```
7. Idempotency check:
```bash
git diff --name-status > reports/compliance/wrk-188-worldenergydata-diff-after-first-apply.txt
git diff --name-only -- worldenergydata specs/repos/worldenergydata > reports/compliance/wrk-188-worldenergydata-scope-after-first-apply.txt
scripts/operations/compliance/migrate_specs_to_workspace.sh --apply --repos worldenergydata
git diff --name-status > reports/compliance/wrk-188-worldenergydata-diff-after-second-apply.txt
git diff --name-only -- worldenergydata specs/repos/worldenergydata > reports/compliance/wrk-188-worldenergydata-scope-after-second-apply.txt
diff reports/compliance/wrk-188-worldenergydata-diff-after-first-apply.txt reports/compliance/wrk-188-worldenergydata-diff-after-second-apply.txt
diff reports/compliance/wrk-188-worldenergydata-scope-after-first-apply.txt reports/compliance/wrk-188-worldenergydata-scope-after-second-apply.txt
test -z "$(git diff --name-only | rg -v '^(worldenergydata/|specs/repos/worldenergydata/|reports/compliance/)' | cat)"
```
8. Submodule pre-commit scope gate and commit:
```bash
git -C worldenergydata add -A
test -z "$(git -C worldenergydata diff --cached --name-only | rg -v '(^|/)specs/' | cat)" 
git -C worldenergydata commit -m "chore(specs): WRK-188 wave1 pointer migration"
SUB_SHA="$(git -C worldenergydata rev-parse HEAD)"
```
9. Hub pre-commit scope gate, governance gate, and commit:
```bash
git add worldenergydata specs/repos/worldenergydata reports/compliance
test "$(git ls-tree HEAD worldenergydata | awk '{print $3}')" = "$SUB_SHA"
test -z "$(git diff --cached --name-only | rg -v '^(worldenergydata$|worldenergydata/|specs/repos/worldenergydata/|reports/compliance/)' | cat)"
scripts/operations/compliance/check_governance.sh --mode gate --scope changed
git commit -m "chore(spec-migration): WRK-188 wave1 worldenergydata apply"
```
10. Publish in one release window:
```bash
git -C worldenergydata symbolic-ref --short HEAD
git -C worldenergydata push
git push
```
11. Post-commit scope audit (defense in depth):
```bash
APPLY_SHA="$(git rev-parse HEAD)"
git diff --name-only "${APPLY_SHA}^..${APPLY_SHA}" | rg -v '^(worldenergydata/|specs/repos/worldenergydata/|reports/compliance/)'
```
Expected output: empty.

Failure policy:
1. Any failed check => stop immediately.
2. If apply already ran, execute rollback.
3. Record failure + command output in WRK-188 progress notes before retry.
4. If `git -C worldenergydata push` succeeds but `git push` fails, immediately attempt a follow-up hub commit that reverts the submodule pointer to last published SHA.
5. If revert push is also blocked (remote/policy outage), freeze further migration writes, record published submodule SHA + blocked hub SHA in WRK-188, and open a containment work item before any retry.

## Done Checklist
- Dry-run log + hash captured and attached to WRK-188.
- No exact or casefold duplicate target paths.
- Source/target file counts match.
- Source/target checksum sets match.
- Pointer README checks pass for every recorded source spec root.
- Cross-review gate passes per normalized verdict rules.
- Idempotency second-apply diff check passed.
- Scope checks pass before and after commit.

## Collision Remediation
1. Inspect `reports/compliance/wrk-188-worldenergydata-target-collisions.txt`, `reports/compliance/wrk-188-worldenergydata-duplicate-targets.txt`, and `reports/compliance/wrk-188-worldenergydata-duplicate-targets-casefold.txt`.
2. Remove or relocate conflicting paths under `specs/repos/worldenergydata/` (or rollback to clean baseline).
3. Re-run dry-run preflight and regenerate compliance artifacts before apply.

## Negative-Path Checks
Run before approval to verify fail-fast behavior:
```bash
test -z "$(cat reports/compliance/wrk-188-worldenergydata-target-collisions.txt)"
test -z "$(cat reports/compliance/wrk-188-worldenergydata-duplicate-targets.txt)"
test -z "$(cat reports/compliance/wrk-188-worldenergydata-duplicate-targets-casefold.txt)"
test -z "$(find worldenergydata -path '*/specs/*' -type l)"
```

## Multi-Provider Workflow Continuity Check
Run before apply:
```bash
timeout 900s scripts/review/cross-review.sh specs/wrk/WRK-188/worldenergydata-wave1-migration.md all --type plan || { echo "cross-review timed out/failed; rerun provider submissions before apply"; exit 1; }
```
Pass condition:
- Reviews confirm migration can proceed while preserving standard workflow:
  - WRK linkage
  - plan approval gate
  - cross-review gate
  - governance checks

## Rollback
1. Revert migration commits in order (submodule first, then hub pointer commit):
```bash
git log --oneline -n 10
# original submodule SHA captured in:
cat reports/compliance/wrk-188-worldenergydata-pre-apply-submodule-sha.txt
git -C worldenergydata revert <submodule_apply_commit_sha>
git revert <hub_apply_commit_sha>
```
2. Re-run file count and source checksum checks on restored state:
```bash
find worldenergydata -type f -path '*/specs/*' | wc -l
find worldenergydata -type f -path '*/specs/*' -print0 | sort -z | xargs -0 sha256sum > reports/compliance/wrk-188-worldenergydata-source-checksums-rollback.txt
```
3. If apply was not committed, restore deterministic scope and re-check:
```bash
test -z "$(git status --porcelain | awk '{print $2}' | rg -v '^(worldenergydata/|specs/repos/worldenergydata/|reports/compliance/)' | cat)"
git restore --staged --worktree worldenergydata specs/repos/worldenergydata
git -C worldenergydata restore --staged --worktree .
git clean -fd -- specs/repos/worldenergydata reports/compliance/wrk-188-worldenergydata-*
python3 - <<'PY'
from pathlib import Path
mf = Path("reports/compliance/wrk-188-worldenergydata-approved-target-files.txt")
if mf.exists():
    for line in mf.read_text().splitlines():
        p = Path(line.strip())
        if p.exists() and p.is_file():
            p.unlink()
for d in sorted(Path("specs/repos/worldenergydata").rglob("*"), reverse=True):
    if d.is_dir():
        try:
            d.rmdir()
        except OSError:
            pass
PY
test -z "$(git status --porcelain)"
```
4. Record rollback reason and reverted SHA in WRK-188 progress notes.
