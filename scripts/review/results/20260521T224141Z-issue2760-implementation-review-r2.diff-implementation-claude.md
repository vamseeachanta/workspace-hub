### Verdict: APPROVE

### Summary
r2 cleanly addresses r1 MAJOR path/provenance findings: the OCIMF "placeholder" heading functions (Cx=1.05·|cos|, Cy=sin, Cm=0.55·sin) are replaced by real Annex A interpolation from a fail-closed, env-var-gated, off-repo licensed workbook with a citation sidecar; grid is rebuilt to the approved issue #2760 contract (3.08 kn default, ±5° heading, 0–28° port rudder), "resultant horizontal force" presentation is removed in favor of explicit X/Y/N components, and a docx artifact plus a private-repo report-layer manifest are added. Test coverage is strong (66 passed; regression-anchored against placeholder constants and removed fields, with a "/mnt/" path-leak guard on the sidecar). A few questions remain around fields the tests reference but that are not visible in the shown diff, and around the brittleness of hard-coded workbook sheet/column indices.

### Issues Found
- [P2] Correctness/test-source mismatch: tests/naval_architecture/test_b1528_sirocco_current_heading_rudder.py asserts row["ocimf_first_cut_cx_current"], row["ocimf_first_cut_cy_current"], row["ocimf_first_cut_cm_current"], but the visible _row() diff only emits ocimf_current_force_*_N / ocimf_current_moment_*_Nm and never assigns ocimf_first_cut_c{x,y,m}_current keys — either these fields are added in a portion of the file not included in the diff (likely, since the header reports 66 passed) or the test would KeyError. Worth verifying the fields are emitted from _row() in the committed source.
- [P2] Performance/correctness: _load_ocimf_workbook_basis() is @lru_cache(maxsize=1) but its inputs (OCIMF_WORKBOOK_PATH env var and the resolved file) are not part of the cache key. If a long-lived process changes the env var or the workbook is replaced, the cache will silently serve stale curves. Acceptable for one-shot report generation; risky if reused in services.
- [P3] Brittleness: _load_ocimf_workbook_basis() hard-codes sheet names ("Data 5a-9a", "Data 10a-14a") and column indices (23/24, 1/7, 9/15) without a schema check. Any workbook reformat will silently change basis values rather than fail loudly. Consider a header-row sanity assertion before trusting columns.
- [P3] UX/error-message: select_ocimf_loaded_tanker_current_basis() rejects WD/T <= 6 with "outside the approved >6 screening bucket" — the message implies the bucket is the only failure, but the function also requires wd_over_t > 0 with a different message. Two close paths could be consolidated and the >6 cutoff should cite where the approval comes from (plan SHA/section).
- [P3] Style: Several new artifacts (citations.json, manifest.json, markdown report) end without a trailing newline (\ No newline at end of file), inconsistent with normal POSIX-style text files and with the existing repo convention shown elsewhere.
- [P3] Documentation drift: The markdown report's `default_speed_policy` says 3.08 kn is the issue default and "plots/tables are bounded to 0..4 kn", but the YAML scenario still lists 0 kn as a sweep speed. Zero speed produces all-zero current/rudder rows; consider whether those rows add value or just dilute counts (990 vs 825 rows).

### Suggestions
- Add a header/schema sanity check inside _load_ocimf_workbook_basis() so a reformatted licensed workbook fails loudly instead of returning silently wrong coefficients.
- Key the lru_cache on the resolved workbook path + mtime (or drop the cache and rely on caller-level memoization) so env var changes invalidate it.
- If ocimf_first_cut_cx_current / cy_current / cm_current are real row fields, expose them in _row() in this diff or call out where they're added; if they're not, the test needs updating before merge.
- Tighten select_ocimf_loaded_tanker_current_basis() to cite the approved plan path/section that authorizes the >6 bucket, so a future reviewer sees the provenance inline.
- Add a regression test that constructs a configuration with WD/T <= 6 and confirms the fail-closed ValueError fires with the >6 cutoff message — this defends the screening boundary.
- Normalize trailing newlines on the new JSON / MD artifacts (pre-commit fixers usually catch this).

### Questions for Author
- Where are ocimf_first_cut_cx_current / ocimf_first_cut_cy_current / ocimf_first_cut_cm_current populated on each row? They are asserted in test_ocimf_current_rudder_and_total_components_are_reported_about_cog but I don't see them assigned in the _row() diff.
- Was 0 kn deliberately included in current_speeds_kn? It produces an all-zero row family and was not present in the prior sweep contract — confirm it's part of the approved #2760 grid.
- Is docs/data/OCIMF_CORPUS_README.md already committed in digitalmodel? The preflight raises FileNotFoundError if it is missing, but the README is not part of this diff.
- Did the 96.89s test run set OCIMF_WORKBOOK_PATH to a real licensed workbook, or a fixture? If a fixture, the curve-value assertions (-0.0324 / 0.03406 / 0.00843) effectively pin the fixture rather than the real OCIMF data and should be labeled.
- select_ocimf_loaded_tanker_current_basis() advertises rejected_alternatives but the resolver only reads cxc from "Data 5a-9a" and cyc/cxyc from "Data 10a-14a" — is there a downstream check that the selected_figures list and the actually-read columns stay in sync, or could a future edit drift them apart silently?
