# Refactor review — primary packages and wiki family

- **Date:** 2026-10-10
- **Status:** Review only. No code was changed and no issues were filed.
- **Client:** N/A. Per-client wikis are referred to collectively as `llm-wiki-<client>`; no client, project or person is named.
- **Scope:** `digitalmodel`, `assetutilities`, `worldenergydata`, `assethold`, `llm-wiki`, and the twelve `llm-wiki-<client>` repositories.
- **Emphasis:** the boundaries between the four packages (what belongs where, shared utilities, dependency direction), and what the client wikis should share with `llm-wiki` (tooling, structure, publication and redaction controls).

## 1. Method

1. A script measured every in-scope repository over its git-tracked files: file and line counts, function and class lengths from the Python AST, test-suite patterns, packaging inventory, imports between subpackages, byte-identical files across repositories, and same-named modules with line similarity. The client wikis were compared from tree listings (path and blob identity) and tooling-only checkouts; wiki pages, data and project content were not read.
2. Nine review lanes, each restricted to read-only tools, read the code against those measurements: one per package, one for `llm-wiki`, one for the largest client wiki, one for package boundaries, one for the wiki family, and one cross-repository lane.
3. The highest-ranked claims were then re-measured independently (section 9). Two reviewer statements did not reproduce and are corrected in place.

Every figure below is either a script measurement or a reviewer statement checked against the code. Where a cause was not confirmed in the code it is labelled a hypothesis. **Confidence** is `verified` when the code was opened and `inferred` when the finding rests on a measurement alone.

Revisions measured: digitalmodel `0b2afd4b`, worldenergydata `b36db045`, assetutilities `17dd3e62`, assethold `0e734cc`, llm-wiki `adfaeddfb`.

## 2. Measured baseline

| Repository | Tracked files | Source lines | Python files | Test files | Files over 1,000 lines | Functions of 80 lines or more | Classes of 400 lines or more |
|---|---|---|---|---|---|---|---|
| digitalmodel | 16,874 | 1,283,723 | 5,205 | 1,886 | 58 | 1,051 | 187 |
| worldenergydata | 5,387 | 715,996 | 2,868 | 1,281 | 26 | 536 | 126 |
| assetutilities | 3,265 | 155,492 | 547 | 169 | 6 | 79 | 23 |
| assethold | 1,837 | 77,303 | 328 | 130 | 2 | 51 | 15 |
| llm-wiki | 50,199 | 98,698 | 404 | 200 | 1 | 19 | 0 |
| llm-wiki-&lt;client&gt; (largest) | 8,741 | 116,077 | 523 | 134 | 12 | 68 | 0 |

Caption: Table 1 — size of each repository. Source lines are physical lines of tracked `.py`, `.sh`, `.ps1`, `.js`, `.ts` and `.bat` files, tests included. Function, class and over-1,000-line counts exclude tests.

| Importer | Imports of assetutilities | Imports of worldenergydata | Imports of digitalmodel |
|---|---|---|---|
| digitalmodel | 164 | 15 | n/a |
| worldenergydata | 153 | n/a | 0 |
| assethold | 47 | 0 | 0 |
| assetutilities | n/a | 0 | 0 |
| llm-wiki-&lt;client&gt; (largest) | 0 | 0 | 61 |

Caption: Table 2 — import statements of each sibling package, counted in Python files.

Byte-identical source files of 1,500 bytes or more shared between the four packages: 46 groups. By pair: assethold and assetutilities 39; digitalmodel and worldenergydata 14; assetutilities and worldenergydata 11; assethold and worldenergydata 10; assethold and digitalmodel 8; assetutilities and digitalmodel 8.

## 3. Package boundaries

### 3.1 What each package is for today, from its code

| Package | Responsibility found in the code |
|---|---|
| assetutilities | Shared base: configuration-driven engine, file, YAML, spreadsheet and plotting helpers, units, and the workflow-API envelope. |
| digitalmodel | Offshore and subsea engineering analysis and solver orchestration. |
| worldenergydata | Acquisition and analysis of public energy data, split into 38 workspace members under `packages/`. |
| assethold | Personal-asset analysis: equities, options, portfolio and property. |

Caption: Table 3 — current responsibility of each package.

### 3.2 Dependency direction

The graph is acyclic. `assetutilities` imports none of its siblings. `worldenergydata`, `assethold` and `digitalmodel` each import `assetutilities`. `digitalmodel` also imports `worldenergydata` (11 statements in `src/digitalmodel/field_development/economics.py`, 4 in its test). No package imports `assethold`.

**Target graph:** unchanged in shape — `assetutilities` at the base, the other three above it, and `digitalmodel → worldenergydata` as a declared optional extra limited to the economics members. No edge needs reversing. The defects are in how the edges are declared and in code that was copied across an edge instead of imported.

### 3.3 Code in the wrong package

| Code | Sits in | Belongs in | Evidence |
|---|---|---|---|
| Equity and portfolio analysis (`specialized/finance/…`, web blueprints) | digitalmodel | assethold | assethold has the maintained `modules/stocks/`; the digitalmodel copies import a top-level `common` package that is not shipped. |
| BSEE data components, field-development components (`ong_fd_components.py`, 1,115 lines) | digitalmodel | worldenergydata | worldenergydata holds maintained versions; line similarity 0.29 for the largest pair. |
| Well-path module (`wellpath3D.py`, 1,986 lines, includes a desktop GUI) | digitalmodel | one owner, to be decided | A decomposed 1,250-line copy sits in worldenergydata; similarity 0.15. |
| Riser, pipeline, wellhead and casing calculations (11 modules under `calculations/`, plus `polynomial`) | assetutilities | digitalmodel | Zero imports of `assetutilities.calculations` from digitalmodel `src`, `tests`, `scripts` or `examples`. Only `polynomial` is used inside assetutilities. |
| Agent tooling (`agent_os/`, `cli/create-spec*`, `devtools/`) | assetutilities (inside the importable package) | workspace tooling, outside the library | About 50 modules; no consumer import was found. |
| Generic readers and legacy components (`common/legacy/`, 26 files with a nested second copy) | worldenergydata core member | BSEE member for the four live callers; delete the remainder | 17 references in 9 files; four are outside the legacy tree. |

Caption: Table 4 — modules that sit outside the responsibility of the package that holds them.

Ninety-eight bare `from common…` or `import common…` statements exist in 33 files under `digitalmodel/src`, and no top-level `common` package is shipped. Those modules cannot be imported from an installed wheel unless a path insertion supplies the package at run time; which of the 33 are reached that way is not established.

### 3.4 Shared utilities implemented more than once

| Concern | Copies | Single source proposed |
|---|---|---|
| Plotting (`Visualization` class) | assetutilities `common/visualizations.py` (910 lines) and digitalmodel `infrastructure/utils/visualization/visualizations.py` (906 lines), similarity 0.93; a third in assethold `common/visualization.py`; digitalmodel reaches the class by three import routes | `assetutilities.common.visualizations` |
| Deep merge and YAML input | `update_deep.py` and `ymlInput.py` in assetutilities and digitalmodel, same logic; the digitalmodel copy keeps a bare `except` | assetutilities |
| Database access | assetutilities `common/database.py` (1,287 lines) and digitalmodel `infrastructure/utils/database.py` (910 lines), similarity 0.42; the bounded-retry fix exists only in assetutilities | assetutilities, after characterisation tests |
| Application manager | assetutilities (499 lines) and digitalmodel (408 lines), similarity 0.32 | assetutilities |
| Data validation (`DataValidator`) | At least five locations; `worldenergydata/src/validators/data_validator.py` is byte-identical to `assetutilities/common/validation.py` | `assetutilities.common.validation` |
| System-file readers | assethold `common/data.py` (364 lines), a copy under assetutilities `docs/`, and worldenergydata `common/legacy/data.py` | assetutilities, with the source-specific reader left in assethold |
| Report template | `plotly_report_template.py` byte-identical in three places across assetutilities and assethold, none of them inside a packaged `src` tree | assetutilities, packaged under `src/` |

Caption: Table 5 — utility code that exists in more than one package.

`digitalmodel/src/digitalmodel/infrastructure/utils/engineering_units.py` is already the right pattern: a thin re-export of `assetutilities.units`.

## 4. Prioritised items

Impact, effort and risk are the reviewers' ratings, checked for consistency across lanes. Effort: **S** under one day, **M** one to five days, **L** more than five days. Wave refers to the sequence in section 7.

| ID | Item | Repositories | Impact | Effort | Risk | Wave | Quick win | Confidence |
|---|---|---|---|---|---|---|---|---|
| P1 | Declare the `digitalmodel → worldenergydata` dependency and reconcile six version ranges that do not overlap | digitalmodel, worldenergydata | High | M | Medium | 2 | no | verified |
| P2 | Stop tests replacing `sys.modules` entries without teardown; record the test order and seed | digitalmodel | High | S | Medium | 1 | yes | verified (mechanism) |
| P3 | Declare the assetutilities public surface with an import-contract test; declare the sibling one way with a floor that contains the imported modules | all four | High | S–M | Low | 1 | yes | verified |
| P4 | Replace digitalmodel's second copy of the assetutilities utility layer with imports | digitalmodel, assetutilities | High | M | Medium | 2–3 | partly | verified |
| P5 | Move misplaced modules to the owning package (Table 4) | all four | High | M | Low–Medium | 2 | partly | verified for files opened |
| P6 | Delete the vendored agent-tooling trees | assetutilities, assethold | High | S | Low | 0 | yes | verified (duplication) |
| P7 | Restore the assetutilities test net: collect the seven directories skipped off Windows; write test output to temporary directories | assetutilities | High | M | Medium | 1 | no | verified |
| P8 | Correct assetutilities runtime dependencies: tooling and browser automation out, missing imports in | assetutilities | High | S–M | Medium | 1 | partly | verified (manifest) |
| P9 | Extend lint, type and security gates from `src/` to `packages/` | worldenergydata | High | M | Medium | 1 | no | verified |
| P10 | Replace three overlapping test-exclusion mechanisms with one audited list | worldenergydata | High | M | Medium | 1 | no | verified |
| P11 | Collapse duplicated scripts and delete module copies the import system cannot reach | worldenergydata | High | S–M | Low | 0 | yes | verified in part |
| P12 | Make workspace members stop importing the root distribution | worldenergydata | High | L | Medium | 3 | no | verified (imports) |
| P13 | Remove legacy forks: the nested `legacy/legacy/` tree, `src/validators`, and the five `DataValidator` copies | worldenergydata, digitalmodel, assetutilities | Medium | M | Medium | 0–2 | partly | verified |
| P14 | Turn the three engine dispatchers into lazy registries | digitalmodel, assetutilities, assethold | High | M | Medium | 2 | partly | verified |
| P15 | Repair assethold packaging metadata and its import-time mocks of 17 third-party modules | assethold | High | S–M | Low–Medium | 0–1 | partly | verified |
| P16 | Adopt one tooling baseline: Python floor, formatter, type-check scope, one pytest configuration per repository | all four | Medium | M | Low | 3 | partly | verified |
| P17 | Stop vendoring harness scripts by copy; two variants already exist | all four | Low–Medium | S | Low | 0 | yes | inferred |
| P18 | Move code and generated output out of `docs/`, `config/` and tracked result trees | assetutilities, digitalmodel, worldenergydata | Medium | M | Low | 2 | partly | verified (presence) |
| P19 | Split oversized modules that mix calculation, user interface and HTML generation | digitalmodel, worldenergydata, assethold | Medium | L | Medium | 4 | no | inferred |
| P20 | Enforce the frontmatter visibility check in CI for every wiki | wiki family | High | M | Medium | 1 | no | verified |
| P21 | Add secret scanning to every wiki | wiki family | High | S | Low | 0 | yes | verified |
| P22 | Issue one redaction, data-cycle and agent-posture baseline from a template, with a drift check | wiki family | High | M | Low | 1 | no | verified |
| P23 | Replace client-local publication gates with one shared, fail-closed implementation and per-client pattern data | wiki family | High | L | Medium | 2 | no | verified |
| P24 | Check content promoted from a client wiki on arrival in the generic wiki | llm-wiki | High | M | Medium | 2 | no | verified |
| P25 | Agree the smallest common wiki skeleton; correct the template ignore rules and the project-instantiation procedure | wiki family | Medium | M | Medium | 1–2 | partly | verified (layout) |
| P26 | Give `llm-wiki` a dependency manifest and a CI job that runs its tests; remove loader and helper copy-paste | llm-wiki | High | S–M | Medium | 1 | partly | verified |
| P27 | In the largest client wiki: declare the `digitalmodel` dependency once; share extractor helpers; bring project test suites into CI | llm-wiki-&lt;client&gt; | High | M | Medium | 2 | partly | verified |
| P28 | Inspect the client-registry copy tracked in three client wikis | wiki family | High if content is the full registry | S | Medium | 0 | yes | file name verified; content not read |

Caption: Table 6 — prioritised refactor items.

## 5. Item detail

### 5.1 Boundaries and dependencies

**P1.** `digitalmodel/pyproject.toml` contains no `worldenergydata` entry, while `src` imports it in 11 statements. The two root manifests cannot be resolved into one environment:

| Package | digitalmodel | worldenergydata |
|---|---|---|
| numpy | `>=1.24.0,<2.0.0` | `>=2.2.6,<3.0` |
| plotly | `==5.17.0` | `>=5.18.0,<6.0` |
| scikit-learn | `==1.3.2` | `>=1.7.2,<2.0` |
| reportlab | `>=5.0.1,<6.0.0` | `>=4.0.0,<5.0` |
| rich | `>=13.0.0,<15.0.0` | `>=15.0.0,<16.0` |
| psutil | `==5.9.6` | `>=7.2.1,<8.0` |

Caption: Table 7 — version ranges that do not overlap.

Whether the two are ever resolved together today, and whether the imports are all guarded, is not established. Decision needed first: whether digitalmodel consumes the economics workspace members only, or the root distribution.

**P3.** The three consumers declare assetutilities three ways: an editable sibling path with floor `>=0.0.7`; a git source on `main`, unpinned, with floor `>=0.1.0`; and a sibling path with no range. assetutilities is at 0.1.1. The `>=0.0.7` floor admits releases without the `workflow_api` and `units` modules that digitalmodel imports. The consumers use roughly fifteen module paths (`common.*`, `engine`, `units`, `constants`, `workflow_api`, one `modules` path); none of that surface is declared or pinned by a test in assetutilities.

**P4, P5, P13.** See Tables 4 and 5. Order within P4: `update_deep` and `ymlInput` first (logic identical), then plotting, then database last, behind characterisation tests on the 24 referencing files. P5 removes callers of the local database and data copies and so shortens P4.

**P12.** Sixteen imports in 11 member files reach subpackages that exist only in the root distribution (`field_development`, `engine`, `validation`, `analysis`). The members are therefore not installable on their own, which is the stated purpose of the split. One member's manifest documents the pattern and leaves the edge undeclared to avoid a member-to-root cycle.

**P14.** `engine()` in digitalmodel is 778 lines: about 20 solver imports at module top, an `if/elif` chain on a name, and a branch that changes argument handling when a test runner is detected. The same eager-import dispatcher exists in assetutilities and assethold. A name-to-callable table resolved lazily removes the reason tests mock the import system (P2) and makes adding a workflow a table entry.

### 5.2 Test debt

**P2.** Measured: 49 `sys.modules[...] =` assignments in 41 digitalmodel test files, 7 at module level. Five engine test files replace about 35 entries with mock objects; `tests/simple_engine_test.py` does so at import and contains no `monkeypatch`, `finally`, `pop` or `patch.dict`. `digitalmodel.engine` is then imported once against mocks and stays cached. The test extra installs `pytest-randomly` and the configuration fixes no seed, so the order in which this happens varies between runs. Three other test files in the same repository already use the correct pattern (a fixture with teardown).

The mechanism is verified in the code. That it accounts for the 198 failures attributed to persistent mocks in digitalmodel#2312 is **not established**: no failure log was available to the review. The settling evidence is one full-suite run with the seed printed, repeated with the same seed after the five files are converted.

**P7.** `tests/conftest.py` in assetutilities drops seven directories from collection on any non-Windows host, and CI runs on Linux. The directories cover plotting, file management and archive handling, which both dependents import. Separately, 302 files are tracked under `tests/modules/**/results/`; the engine resolves its output directory to the input file's directory, so each test run rewrites tracked files, and many of those tests assert only that a result is not `None`. The engine already accepts a root-folder parameter that a shared fixture can point at a temporary directory.

**P10.** worldenergydata excludes tests through `norecursedirs`, twelve `--ignore` options, and a collection hook in `tests/conftest.py` that also hard-codes twenty files and one whole unit-test directory of 51 files. The pass count therefore does not state what the suite covers.

**P15.** assethold's `tests/conftest.py` replaces 17 third-party modules in `sys.modules` for the whole session, so charting and data-provider code is exercised only against mocks that accept any call. Its console-script entry point does not resolve, and the version string is defined in two places.

**P16 (test configuration).** A `pytest.ini` shadows `[tool.pytest.ini_options]` in three of the four repositories; in two of them the shadowed table holds the coverage threshold, which therefore does not apply.

### 5.3 Duplication and dead code

**P6.** `.agent-os` is 96 files and 26,256 source lines in assetutilities and 161 files and 18,590 lines in assethold; 39 files are byte-identical between them; both were last committed on 2026-03-25; a dated backup file is tracked in both. Correction to the reviewer statement: three non-Python files under `assethold/src` mention the tree (two shell scripts and one JSON template). No Python import of it was found. Those three references need a check before deletion.

**P11.** worldenergydata `scripts/` holds 495 files and 86,684 lines. Five large report functions appear with identical line counts in a root script and a domain copy. `src/worldenergydata/modules/` holds at least 2,290 lines in copies that the import system cannot reach.

**P17.** Five harness scripts are byte-identical in all four packages; two helper scripts exist in two variants, split two repositories each. All four pre-commit configurations already reference files in the parent workspace checkout, so a parent-owned location is established practice.

**P18.** In assetutilities the library that the dependents import is 50,146 of 155,492 source lines; legacy source and vendored JavaScript under `docs/` and the agent tooling account for most of the remainder.

### 5.4 Packaging and tooling

**P8.** assetutilities declares 37 runtime dependencies. No import was found in its `src` for a web framework, three browser-automation packages, or the release tools `build`, `twine` and `bumpver`; `ruff` is listed as a runtime dependency and again under `dev`. Imported and not declared: `colorama`, `PIL`, `sqlalchemy`, `pyodbc`, `psycopg2`. Every consumer installs the declared set transitively. The scan covered direct import statements only.

**P9.** worldenergydata CI runs black and isort on `src/ tests/`, flake8 and bandit on `src/`, and mypy on `src/worldenergydata/`. `src` holds 36,131 source lines; `packages` holds 288,773.

**P16.**

| Repository | Python floor | Formatter and linter | Type checking |
|---|---|---|---|
| digitalmodel | 3.11 | ruff, restricted to four path patterns | mypy hook |
| assetutilities | 3.9 | black and isort configured; ruff run by the hook | strict flags set alongside `ignore_errors`, so nothing is reported |
| worldenergydata | 3.10 | black, isort, flake8; line length 88 against 100 | mypy limited to a path that has since moved |
| assethold | 3.9 | black and isort configured; ruff run by the hook | Python version unset |

Caption: Table 8 — tooling configuration across the four packages. Three of the four already set the uv interpreter to 3.11.

## 6. Wiki family

### 6.1 Measured state

- Twelve client wikis range from 2 to 17,634 tracked files. By layout: 2 follow the hub template, 3 follow it in part, 4 use a different layout, 1 is an empty stub, and 2 are not client engagements (a coordination workspace and a pack-distribution repository).
- **No tooling path is byte-identical between any client wiki and the generic wiki.** Of 660 client tooling paths, 648 exist in exactly one wiki. `README.md` is the only path present in all twelve, and it exists in more than one version.
- Redaction-posture and data-cycle files exist in 2 of 12 client wikis, in two versions. The hub template is a third version and still describes the generic wiki as public.
- No wiki tracks a pre-commit configuration. Nine of twelve client wikis have no CI workflow. None of the 8 workflow files in the family names a secret scanner.
- The `projects/` folder convention appears in 2 of 12; the project template folder in 1 of 12.

### 6.2 What the client wikis should share with `llm-wiki`

| Shared asset | Delivery mechanism | Stays per client |
|---|---|---|
| Visibility-frontmatter check, secret scan, file-size check (P20, P21) | One reusable CI workflow in the hub, called by a short workflow in each wiki | The allow-list file |
| Redaction posture, data-cycle rules, agent posture, ignore rules (P22, P25) | A template rendered into each wiki, with a hash-based drift check | A clearly marked override section |
| Publication gate: leak check, redaction lint, pages builder (P23) | A package in the generic wiki, installed as a tool | Pattern data file; the decision to publish |
| Document extractors (P27 and the family lane) | The same package, as a command-line tool | None |
| Skeleton and project template (P25) | The bootstrap command, plus a command that adds a project | Content directories beyond the skeleton |

Caption: Table 9 — proposed single sources for the wiki family.

### 6.3 Publication and redaction controls, ranked by exposure

1. **P20.** The frontmatter visibility check runs only where a per-host installer has written an untracked hook, and that installer skips any dirty checkout. No workflow invokes it. Its path filter covers three directory names, while the content directories in use across the family include five others. It degrades open in four conditions, including a missing registry.
2. **P23.** Two client wikis publish outward. Their gates are separate implementations; one runs its redaction lint with `continue-on-error`, and one guards a public site with five hard-coded patterns. Redaction patterns are hard-coded in source in one wiki.
3. **P21.** No secret scanning exists anywhere in the family. Credential filename patterns appear in the ignore rules of 2 of 12.
4. **P24.** The gate for promoting content from a client wiki to the generic one is a written procedure only. Nothing on the receiving side checks for client identifiers or links into client repositories.
5. **P22.** Ten of twelve client wikis carry no redaction or data-cycle statement.
6. **P28.** A file named `.workspace-hub/client-wikis.yml` is tracked in three client wikis. The installer that writes it also adds the directory to the ignore rules; in these three that step did not complete. The content was not read. If it is the full registry, a list of clients is committed inside per-client repositories, which the routing rule prohibits. Inspection comes before any other wiki work.

### 6.4 `llm-wiki` tooling (P26)

No CI job runs the test suite and no manifest declares its dependencies. Module-loader boilerplate is repeated in 151 test files; JSON, JSONL and hashing helpers are re-declared in up to 17 scripts under `scripts/ingest/`. The coordination helper that other repositories depend on writes its lock metadata non-atomically and treats a lock directory without metadata as held indefinitely. A file-length cap of 400 lines, enforced by a test, has produced compressed formatting and artificial module splits; a per-function limit already exists in the same test.

## 7. Proposed sequence

| Wave | Purpose | Items | Gate before the next wave |
|---|---|---|---|
| 0 | Remove dead weight and close the cheapest control gaps; nothing here changes behaviour | P6, P11, P17, P21, P28, quick parts of P13 and P15 | Suites pass unchanged; duplicate count re-measured |
| 1 | Make the test and CI signal trustworthy before code moves | P2, P3, P7, P8, P9, P10, P20, P22, P26 | A full-suite run per package with the seed recorded; contract test green in all three consumers |
| 2 | Move code across package boundaries, behind the wave-1 signal | P1, P5, P4 (identical-logic modules), P14, P18, P23, P24, P25, P27 | Both consumers resolve and test against the slimmed assetutilities |
| 3 | Structural work that depends on wave 2 | P4 (database, application manager), P12, P16 | n/a |
| 4 | Decomposition of oversized modules, one module per change | P19 | n/a |

Caption: Table 10 — proposed order of work.

Ordering constraints that matter: P2 precedes P14 and P4, because the engine is the main consumer of the modules being unified and its tests currently cannot fail on a change in assetutilities. P3 precedes every move across a package boundary. P6 precedes any formatter change, so dead code is not reformatted. P25's choice of content root precedes P20's path filter.

## 8. Quick wins

Each is rated effort S with low risk by its reviewer.

1. Delete `.agent-os` and its satellites from assethold and assetutilities, after checking the three non-Python references (P6).
2. Add a secret-scanning workflow to every wiki (P21).
3. Inspect the tracked registry copy in three client wikis (P28).
4. Move the mock installs in five digitalmodel engine test files into one fixture with teardown, and print the random seed in CI (P2).
5. Add an import-contract test in assetutilities over the module paths its consumers use (P3).
6. Raise every assetutilities floor to the first release that contains `workflow_api`, and declare the sibling one way (P3).
7. Move `build`, `twine`, `bumpver` and `ruff` out of assetutilities runtime dependencies; delete `poetry.lock` and stale requirements files (P8, P16).
8. Delete `legacy/legacy/` and `src/validators` in worldenergydata; import the validator from assetutilities (P13).
9. Delete the unreachable module copies and the root-level duplicate scripts in worldenergydata (P11).
10. Replace `update_deep` and `ymlInput` in digitalmodel with re-exports (P4).
11. Fix the assethold console-script target and single-source its version (P15).
12. Reference harness scripts from the parent workspace and delete the vendored copies (P17).
13. Correct the wiki template ignore rules so that as-received data under `data/<dataset>/raw/` is not ignored, and correct the project-instantiation procedure (P25).
14. Keep one pytest configuration per repository (P16).

## 9. Independent checks

| Claim | Check | Result |
|---|---|---|
| Six version ranges do not overlap (P1) | Both root manifests read by script | Reproduced |
| digitalmodel does not declare worldenergydata (P1) | Count of the name in the manifest; count of import statements in `src` | 0 declarations; 11 imports |
| assetutilities declared three ways (P3) | Three manifests read by script | Reproduced; version 0.1.1 |
| 49 assignments in 41 files; no teardown in the main offender (P2) | Pattern count over `tests/`; search for teardown constructs | 49 in 41; 0 teardown constructs |
| `engine()` is 778 lines (P14) | Python AST | 778 |
| Lint gates cover `src/` only (P9) | CI workflow lines; measured line counts | Reproduced; 36,131 against 288,773 |
| 98 bare `common` imports in 33 files (3.3) | Pattern count over `src/` | 98 in 33; no top-level `common` directory |
| No digitalmodel import of `assetutilities.calculations` (Table 4) | Search of `src`, `tests`, `scripts`, `examples` | 0; this settles a question the reviewer left open for three of those trees |
| Tracked test output in assetutilities (P7) | `git ls-files` | 302 tracked files; the reviewer's figure of 324 counted the working tree |
| `.agent-os` unreferenced in `assethold/src` (P6) | Search of `src` | **Not reproduced as stated:** 3 non-Python files mention it; no Python import |
| No secret scanner in any wiki workflow (P21) | Search of all 8 workflow files | 0 of 8 |
| Registry copy tracked in three client wikis (P28) | Tree listings | File name confirmed in 3; content not read |

Caption: Table 11 — claims re-measured after the review lanes reported.

## 10. Not established

- The share of the digitalmodel full-suite failures caused by persistent mocks. Evidence that would settle it: a seeded full-suite run before and after converting the five engine test files.
- Whether digitalmodel and worldenergydata are ever resolved into one environment, and whether every worldenergydata import in the economics module is guarded.
- Which of the 33 digitalmodel files with bare `common` imports are dead and which are reached through a path insertion. An import smoke test over every module of the built wheel would list them.
- Whether the web application in digitalmodel registers the finance and BSEE blueprints, which decides whether P5 is a deletion or a move for those files.
- Whether the in-package and top-level calculation tests in assetutilities are duplicates, and which set CI runs.
- Unused status of each assetutilities runtime dependency: dynamic imports and use from `tests/` or `scripts/` were not scanned.
- Overlap between unit-conversion constants in worldenergydata and the assetutilities units registry; overlap in logging and caching helpers. Not assessed.
- The content of the registry copy in three client wikis.
- Pass or fail state of any excluded or uncollected test population. No test was executed by this review.

## 11. Limits

- No test, build or dependency resolution was run. Statements about behaviour at run time are drawn from reading code and configuration.
- Each review lane read on the order of sixty files. Findings marked `inferred` rest on measurements and names.
- Line similarity is a text measure; two files at 0.42 may differ in behaviour in ways the figure does not show.
- Client wikis other than the largest were reviewed from tooling paths only. Their content, and therefore the adequacy of any redaction actually applied, was outside the review.
- Impact, effort and risk are reviewer judgements, not measurements.
