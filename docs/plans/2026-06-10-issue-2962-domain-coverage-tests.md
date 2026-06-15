# Plan for #2962: domain-coverage guard — TDD test suite for domain_coverage.py

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-06-10
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2962
> **Client:** N/A
> **Review artifacts:** scripts/review/results/2026-06-10-plan-2962-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

### Existing repo code

- Found: `scripts/kanban/domain_coverage.py` — full implementation (244 lines) of all 4 checks: `analyze()` pure core, `render()` Markdown formatter, `load_taxonomy()` YAML parser, `main()` CLI. `analyze()` takes an injectable `runner` parameter making it hermetically testable without live GitHub calls.
- Found: `.github/workflows/domain-coverage.yml` — daily scheduled workflow; mints App-token, fetches deckhand taxonomy, runs `domain_coverage.py --taxonomy /tmp/taxonomy.yaml | tee "$GITHUB_STEP_SUMMARY"`. Fully wired; no code changes needed to the workflow.
- Gap: `tests/kanban/` directory does not exist (confirmed: `ls tests/kanban/` → "No such file or directory"). `tests/kanban/test_domain_coverage.py` does not exist — zero test coverage for the guard.
- Found: `scripts/kanban/reconcile.py`, `scripts/kanban/relabel.py` — sibling scripts with no tests; out of scope for this plan.

### Standards

Not applicable.

### LLM Wiki pages consulted

No relevant wiki pages.

### Documents consulted

- Issue [#2962](https://github.com/vamseeachanta/workspace-hub/issues/2962) body — defines the 4 invariant checks, the warn-only output contract (exit 0 by default), and the verification baseline ("audit pass of 2026-06-07 returned `no_domain=[] multi=[]` for all 17 repos").
- `docs/plans/2026-05-02-label-taxonomy-gap.md` — prior label taxonomy audit that established the `domain:` prefix family (161 labels); confirms `DOMAIN_PREFIX = "domain:"` in `domain_coverage.py` reflects the canonical convention.
- `scripts/kanban/domain_coverage.py` docstring (lines 1–30) — defines `DEFAULT_REPOS` (17 repos), `--strict` exit-1 contract, and the injectable runner pattern used throughout.

### Gaps identified

- No tests for `domains_of()` helper.
- No tests for `analyze()` pure core (4 classification paths: zero, multi, unknown, alias; taxonomy-absent degradation).
- No tests for `render()` (clean-state checkmark, per-repo violation detail, taxonomy-missing notice).
- No tests for `load_taxonomy()` (canonical + alias parsing from YAML).
- No integration tests for `main()` CLI (warn-only exit 0, `--strict` exit 1, `--repos` file override).
- `tests/kanban/` directory must be created.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-06-10T via `mcp__github__issue_read`):
- `#2962` — OPEN — "Domain-coverage guard: nightly check that every open issue has exactly one taxonomy-known domain: label (all 17 repos)"

**File existence** (verified 2026-06-10T):
- EXISTS: `scripts/kanban/domain_coverage.py`
- EXISTS: `.github/workflows/domain-coverage.yml`
- EXISTS: `docs/plans/2026-05-02-label-taxonomy-gap.md`
- MISSING (new — this plan creates): `tests/kanban/test_domain_coverage.py`

**Gap proofs**:
- `ls /home/user/workspace-hub/tests/kanban/ 2>&1` → "No such file or directory" → `tests/kanban/` does not exist.
- `ls /home/user/workspace-hub/tests/kanban/*.py 2>&1` → confirmed: zero test files.

**Line excerpts** (`domain_coverage.py` key surfaces, verified via `Read` tool):
```python
# line 44
DOMAIN_PREFIX = "domain:"

# line 49–67 — 17 repos in DEFAULT_REPOS confirmed
DEFAULT_REPOS = [
    "vamseeachanta/aceengineer-admin",
    "vamseeachanta/aceengineer-strategy",
    "vamseeachanta/achantas-data",
    "vamseeachanta/assetutilities",
    "vamseeachanta/deckhand",
    "vamseeachanta/deckhand-sandbox",
    "vamseeachanta/digitalmodel",
    "vamseeachanta/hobbies",
    "vamseeachanta/investments",
    "vamseeachanta/llm-wiki",
    "vamseeachanta/llm-wiki-mkt-a",
    "vamseeachanta/llm-wiki-fdas",
    "vamseeachanta/sabithaandkrishnaestates",
    "vamseeachanta/teamresumes",
    "vamseeachanta/workspace-hub",
    "vamseeachanta/worldenergydata",
    "samdansk2/assethold",
]

# line 79 — injectable runner makes analyze() hermetically testable
def analyze(issues: list[dict], canonical: set[str] | None, aliases: set[str] | None) -> dict:
```

**Reproduction proofs**:
N/A — this plan creates a test suite for a working implementation; no runtime failure exists.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-06-10-issue-2962-domain-coverage-tests.md` |
| Implementation (existing, no change) | `scripts/kanban/domain_coverage.py` |
| Workflow (existing, no change) | `.github/workflows/domain-coverage.yml` |
| Tests (new) | `tests/kanban/test_domain_coverage.py` |
| Plan review — Claude | `scripts/review/results/2026-06-10-plan-2962-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-06-10-plan-2962-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-06-10-plan-2962-gemini.md` |

---

## Deliverable

`tests/kanban/test_domain_coverage.py` with ≥15 hermetic tests covering all 4 analysis checks, renderer output, taxonomy loading, and CLI entry point — no live GitHub API calls anywhere in the suite.

---

## Pseudocode

```python
# --- Fixture helpers (module-level, used by multiple tests) ---

def make_issue(number, title, domain_labels: list[str]) -> dict:
    return {
        "number": number, "title": title,
        "labels": [{"name": f"domain:{d}"} for d in domain_labels],
    }

def make_taxonomy_yaml(canonical: list[str], aliases: list[dict]) -> str:
    # canonical: ["ops", "ci", "testing"]  (keys of crosswalk)
    # aliases: [{"alias": "old-name", "canonical": "new-name"}]
    return yaml.dump({
        "crosswalk": {c: {} for c in canonical},
        "aliases": aliases,
    })

# --- analyze() tests: pure core, no I/O ---

def test_analyze_zero_domain_issue():
    result = analyze([make_issue(1, "no domain", [])], canonical={"ops"}, aliases=set())
    assert result["zero"] == [{"number": 1, "title": "no domain", "domains": []}]
    assert result["multi"] == [] and result["unknown"] == [] and result["alias"] == []

# --- render() tests: string output from a report dict ---

def test_render_all_clean_shows_checkmark():
    report = {"repos": {"r/x": {"total":1, "zero":[], "multi":[], "unknown":[], "alias":[],
                                 "taxonomy_checked": True}},
              "any_taxonomy": True}
    md, total = render(report)
    assert "✅ Invariant holds" in md and total == 0

# --- load_taxonomy() tests: file I/O via tmp_path ---

def test_load_taxonomy_parses_canonical_and_aliases(tmp_path):
    p = tmp_path / "taxonomy.yaml"
    p.write_text(make_taxonomy_yaml(["ops", "ci"], [{"alias": "old", "canonical": "ops"}]))
    canonical, aliases = load_taxonomy(p)
    assert canonical == {"ops", "ci"} and aliases == {"old"}

# --- main() integration: fake gh binary stub, subprocess call ---

def test_main_strict_exits_1_with_violations(tmp_path):
    # stage fake gh that returns one no-domain issue for a single repo
    # call main() as subprocess with --repos pointing at that single repo
    # assert returncode == 1
    ...
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `tests/kanban/test_domain_coverage.py` | TDD test suite — all surfaces of domain_coverage.py |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_domains_of_strips_prefix` | `domains_of()` strips `domain:` and returns bare names | issue with labels `domain:ops`, `priority:high` | `["ops"]` |
| `test_domains_of_ignores_non_domain_labels` | labels without `domain:` prefix are ignored | issue with only `priority:high` | `[]` |
| `test_analyze_zero_domain_issue` | issue with no domain → zero bucket | `[make_issue(1, "x", [])]`, canonical=`{"ops"}` | `zero=[{number:1,...}]`, others empty |
| `test_analyze_single_known_domain_clean` | one known domain → no violations | canonical=`{"ops"}`, issue with `domain:ops` | all 4 buckets empty |
| `test_analyze_multi_domain_issue` | >1 domain → multi bucket | issue with `domain:ops`, `domain:ci` | `multi` non-empty, `zero` empty |
| `test_analyze_unknown_domain_issue` | domain not in canonical → unknown bucket | canonical=`{"ops"}`, issue with `domain:unknown` | `unknown=[{..., label:"unknown"}]` |
| `test_analyze_alias_domain_issue` | domain in aliases → alias bucket (not unknown) | aliases=`{"old"}`, issue with `domain:old` | `alias=[{..., label:"old"}]`, `unknown=[]` |
| `test_analyze_taxonomy_none_skips_unknown_and_alias` | None taxonomy → only zero/multi checked | `canonical=None, aliases=None`, issue with unknown domain | `unknown=[], alias=[], taxonomy_checked=False` |
| `test_render_all_clean_shows_checkmark` | zero violations → ✅ line in output | clean report dict | `"✅ Invariant holds"` in md, `total==0` |
| `test_render_violations_shows_per_repo_detail` | violation rows appear per repo | one repo with one zero-domain issue | repo section with `**zero**` detail line |
| `test_render_taxonomy_not_checked_notice` | `any_taxonomy=False` → notice in header | `report["any_taxonomy"]=False` | `"taxonomy.yaml not provided"` in header |
| `test_load_taxonomy_parses_canonical_and_aliases` | YAML → `(canonical_set, aliases_set)` | YAML with 2 canonical + 1 alias | `({"ops","ci"}, {"old"})` |
| `test_default_repos_count_is_17` | `DEFAULT_REPOS` matches 17-repo scope | N/A (import only) | `len(DEFAULT_REPOS) == 17` |
| `test_main_warn_only_exit_0_with_violations` | violations present + no `--strict` → exit 0 | fake gh returns no-domain issue, no --strict | `returncode == 0` |
| `test_main_strict_exits_1_with_violations` | violations present + `--strict` → exit 1 | fake gh returns no-domain issue, `--strict` flag | `returncode == 1` |

---

## Acceptance Criteria

- [ ] `tests/kanban/test_domain_coverage.py` exists with ≥15 tests.
- [ ] All tests are hermetic — no live GitHub API calls (fake gh binary injected via PATH for main() integration tests; pure functions tested directly).
- [ ] `uv run pytest tests/kanban/test_domain_coverage.py -v` passes green.
- [ ] `test_default_repos_count_is_17` locks DEFAULT_REPOS to the issue's 17-repo scope.
- [ ] No regression: `uv run pytest tests/ -x` passes.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | pending | — |
| Codex | pending | — |
| Gemini | pending | — |

**Overall result:** pending

---

## Risks and Open Questions

- **Risk:** `load_taxonomy()` requires PyYAML; the module guards with `try/except ImportError: yaml = None`. Test environment must have `pyyaml` installed (it is declared in the workflow's `pip install pyyaml` step). Confirm it appears in `pyproject.toml` dev-dependencies or install in test setup.
- **Risk:** Fake-gh stub for `main()` integration tests must write argv to a temp log file (same pattern as `tests/review/test_attest_plan_claims.py`'s `_make_fake_gh`). Reuse that pattern to avoid reinventing it.
- **Open:** Should `tests/kanban/__init__.py` be created? Current `tests/` layout uses pytest auto-discovery without `__init__.py`; do not create unless test imports fail without it.
- **Open:** `reconcile.py` and `relabel.py` also lack tests. Out of scope for #2962; file follow-on issues if desired.

---

## Complexity: T2

New test file (≥15 tests) covering 5 function surfaces across a 244-line module. Requires constructing fake-gh binary stubs and YAML fixtures. Touches one new file; existing implementation and workflow unchanged.
