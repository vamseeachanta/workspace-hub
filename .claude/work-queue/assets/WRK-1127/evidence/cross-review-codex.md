# Codex Cross-Review — WRK-1127 Feature-First Planning

**Reviewer:** Codex
**Date:** 2026-03-11
**Stage:** 6 — Cross-Review
**Artifact reviewed:** `specs/wrk/WRK-1127/wrk-1127-feature-first-planning.md`

---

## Review Scope

Script correctness (bash patterns, sed/grep reliability, YAML parsing), edge cases
in `new-feature.sh` (empty children list, `wrk_ref` not found, `next-id.sh` race),
and the `dep_graph.py` extension approach.

---

## 1. Bash Pattern Analysis — new-feature.sh

### 1.1 Decomposition table parsing

```bash
while IFS='|' read -r _ key title scope deps agent wrk_ref _; do
```

This splits on `|` and discards the leading/trailing empty fields produced by
Markdown table syntax (`| col1 | col2 |`). The trailing `_` absorbs any extra
pipe-delimited columns gracefully.

**Issue (MINOR-1): Pipe characters inside cell values break the IFS split.**
Markdown table cells containing literal `|` (e.g. a title like `"Auth | Login"`)
would split incorrectly. For the current decomposition table in WRK-1127 this is
not a risk (no cells contain `|`), but future feature authors could trigger this.
A comment in the script warning against `|` in decomposition cells would be helpful.

### 1.2 `grep '^|'` source line

```bash
done < <(grep '^|' "$SPEC_REF" | grep -v 'Child key\|---')
```

This correctly anchors to lines starting with `|` and filters the header and
separator rows. However:

**Issue (MINOR-2): `grep -v 'Child key\|---'` also filters any content rows that
happen to contain `---` or the substring `Child key` within a cell.**
For example, a child title like `"Resolve Child key conflicts"` would be silently
dropped. The separator filter should be more precise:

```bash
grep -v '^|-\{3\}'   # only rows where the second character is a dash (separator rows)
```

Combined with `grep -v '| Child key'` (anchored). This is low probability but
worth noting.

### 1.3 Whitespace stripping

```bash
key="${key// /}"
title="${title## }"; title="${title%% }"
```

This strips leading/trailing single spaces. Markdown tables routinely pad cells
with multiple spaces for alignment (e.g. `| child-a      | ...`). The `## ` and
`%% ` patterns strip only a single space. Use `"${title##+( )}"` (extglob) or:

```bash
title="$(echo "$title" | sed 's/^ *//;s/ *$//')"
```

**Issue (MINOR-3):** Multi-space padding will leave trailing spaces in `title` and
`scope` fields, which appear verbatim in generated child WRK `.md` frontmatter.
The generated `title:` YAML field will have trailing spaces, which is valid YAML
but visually inconsistent.

### 1.4 children array serialization

```bash
CHILDREN_YAML="[$(IFS=', '; echo "${CHILDREN[*]}")]"
```

This works correctly in bash when `CHILDREN` has at least one element. When
`CHILDREN` is empty (no rows parsed):

```bash
CHILDREN_YAML="[]"   # because ${CHILDREN[*]} expands to empty string
```

Result would be `[  ]` with the IFS separator, not `[]`. This is then:

```bash
sed -i "s/^children: \[\]/children: [  ]/" "$WRK_FILE"
```

**Issue (MINOR-4): Empty children edge case.** If the decomposition table has zero
valid rows (all filtered or file not found), `CHILDREN_YAML` becomes `[ ]` (one
space), not `[]`, and the `sed` replacement will insert `[ ]` into the frontmatter.
Guard with:

```bash
if [[ ${#CHILDREN[@]} -eq 0 ]]; then
  echo "WARNING: no children parsed — frontmatter unchanged" >&2
  exit 1
fi
```

### 1.5 wrk_ref not found — WARNING and continue vs. exit

```bash
echo "WARNING: wrk_ref ${wrk_ref} not found — skipping adoption" >&2
```

The script emits a warning and continues to the next row. This means the feature
WRK's `children:` list will be missing the intended adopted item. The user gets a
summary line that omits the skipped item but does not clearly indicate the
`children:` list is incomplete. A non-zero exit or an explicit `FAIL=1` accumulator
with a final `exit $FAIL` would be safer — missing an adoption silently is harder
to detect than a script exit.

**Issue (MINOR-5):** The skip-and-continue behaviour on failed adoption may produce
a silently incomplete `children:` list. Either exit non-zero, or print a clear
"INCOMPLETE — re-run after resolving missing WRK" footer.

### 1.6 next-id.sh race condition

`next-id.sh` is called once per new child in a sequential loop. Because the loop is
sequential (not parallel), and `next-id.sh` updates a state file atomically, there
is no parallel race. The sequential risk is that two concurrent invocations of
`new-feature.sh` (two terminal sessions running simultaneously) could produce
duplicate IDs. This is the same risk that exists for any call to `next-id.sh` and
is out of scope for this plan to fix. The plan's triage correctly identifies this
as pre-existing and acceptable.

**No new race introduced** by the plan's sequential loop pattern.

---

## 2. sed/grep Reliability Analysis

### 2.1 SPEC_REF extraction

```bash
SPEC_REF=$(grep '^spec_ref:' "$WRK_FILE" | sed 's/spec_ref: *//' | tr -d '"')
```

Correctly strips the `spec_ref:` prefix and removes surrounding quotes. Works for
both quoted (`spec_ref: "path"`) and unquoted (`spec_ref: path`) YAML scalar values.
Handles leading spaces in the value via `sed 's/spec_ref: *//'`.

### 2.2 category/subcategory extraction

```bash
PARENT_CAT=$(grep '^category:' "$WRK_FILE" | awk '{print $2}' | tr -d '"')
```

`awk '{print $2}'` extracts the second whitespace-delimited field. For
`category: harness` this gives `harness`. For `category: ""` (empty quoted) this
gives `""` which after `tr -d '"'` becomes an empty string — then defaulted to
`uncategorised`. Correct behaviour.

### 2.3 Parent insertion sed

```bash
sed -i "s/^id: ${wrk_ref}/id: ${wrk_ref}\nparent: ${WRK_ID}/" "$EXISTING"
```

GNU sed (Linux) handles `\n` in replacement strings correctly. The pattern anchors
to `^id:` so it will not match `child-id:` or other keys. If a WRK file has
`id: WRK-032` followed by an existing `parent:` line, the `grep -q '^parent:'`
guard prevents a second insertion. Correct.

### 2.4 status update sed

```bash
sed -i "s/^status: pending/status: coordinating/" "$WRK_FILE"
```

If the feature WRK already has `status: working` (moved to working dir during
Stage 8), this sed pattern will not match and the status will remain `working`.
This is technically correct — `new-feature.sh` is expected to be called at Stage 7
exit when the status is still `pending`. The plan should document that
`new-feature.sh` must be called before Stage 8 claim-activation.

---

## 3. YAML Parsing Correctness

### 3.1 chunk-sizing.yaml

The plan's YAML content is valid. The `version: "1.0"` key will parse as a string
(quoted), not a float — correct for a version identifier. All keys are scalars.
The verification step `yaml.safe_load(open(...))` is appropriate.

### 3.2 stage-09-routing.yaml addition

The proposed `feature_routing:` block:

```yaml
feature_routing:
  condition: "frontmatter.type == 'feature' and stage7_complete"
  action: |
    Run: scripts/work-queue/new-feature.sh WRK-NNN
    Set status: coordinating
    Log: "Feature WRK-NNN decomposed into N children"
  next_stage: null
```

This is valid YAML. The `|` literal block scalar for `action` is correct syntax.
`next_stage: null` is valid. The YAML parse verification in Task 11 will catch
any syntax errors before commit.

### 3.3 children: list parsing in feature-close-check.sh and feature-status.sh

```bash
CHILDREN=$(grep '^children:' "$WRK_FILE" | sed 's/children: *\[//;s/\]//' | tr ',' ' ')
```

This handles the inline YAML list format `children: [WRK-1128, WRK-1129]`. It does
NOT handle block-sequence YAML format:

```yaml
children:
  - WRK-1128
  - WRK-1129
```

**Issue (MINOR-6):** If `new-feature.sh` ever produces children in block-sequence
format (it currently produces inline `[...]` via the `CHILDREN_YAML` variable), or
if a user hand-edits the frontmatter to block format, `feature-close-check.sh` and
`feature-status.sh` will silently parse zero children and report PASS incorrectly.
A comment noting the inline-list-only assumption would guard against this.

---

## 4. dep_graph.py Extension Approach

The plan specifies using a **separate `FeatureTreeItem` dataclass** rather than
extending `WRKItem`. This is the correct approach because:

1. `WRKItem` is consumed by `compute_graph()` which only accesses `blocked_by`.
   Adding `type`, `children`, `parent` to `WRKItem` would not break callers, but
   it would add unused fields to the hot path for non-feature items.
2. A separate dataclass makes the feature rendering path clearly isolated — easier
   to test and easier to remove if the approach changes.

**The plan does not specify where `FeatureTreeItem` is added in the file.** Given
`dep_graph.py` is 370 lines, child-b should insert the new dataclass after the
existing `GraphResult` dataclass (line ~35) and add the `--feature` flag to the
`argparse` block at the start of `main()`. No existing function signatures change.

**Issue (MINOR-7):** The `_discover_items_for_feature()` helper must locate the
feature WRK file across `pending/`, `working/`, `blocked/`, and potentially
`archive/` directories (the feature WRK moves to `working/` at Stage 8). The plan
does not specify this search scope. The analogous pattern in `feature-status.sh`
searches `pending`, `working`, `blocked`, and falls back to `archive`. The
`dep_graph.py` implementation should follow the same search order.

---

## 5. Summary of Findings

| ID | Severity | Finding |
|----|----------|---------|
| MINOR-1 | MINOR | Pipe chars in decomposition cell values break IFS split; add comment |
| MINOR-2 | MINOR | `grep -v 'Child key\|---'` may filter valid content rows; tighten pattern |
| MINOR-3 | MINOR | Single-space strip leaves multi-space padding in generated frontmatter |
| MINOR-4 | MINOR | Empty CHILDREN array produces `[ ]` not `[]`; add guard |
| MINOR-5 | MINOR | Skip-and-continue on failed adoption produces silent incomplete children: list |
| MINOR-6 | MINOR | Block-sequence YAML children format not handled in close-check/status scripts |
| MINOR-7 | MINOR | dep_graph.py --feature search scope across WRK state dirs not specified |

No MAJOR findings. The bash patterns are sound for the target environment (GNU/Linux,
bash 5+). The YAML parse verification steps are appropriate. The `dep_graph.py`
extension approach is architecturally correct.

---

## Verdict: APPROVE

All findings are MINOR and addressable during child WRK execution. No pattern is
fundamentally broken on the target platform. The script logic is correct for the
primary (happy) path, and the identified edge cases are low-probability in normal
usage.
