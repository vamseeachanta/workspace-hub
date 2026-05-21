OpenAI Codex v0.132.0
--------
workdir: /mnt/local-analysis/agent-worktrees/workspace-hub-issue-2747-promotion-ledger
model: gpt-5.5
provider: openai
approval: never
sandbox: workspace-write [workdir, /tmp, $TMPDIR]
reasoning effort: medium
reasoning summaries: none
session id: 019e4aea-133b-7d90-890c-be21864a9d4c
--------
user
# Codex Adversarial Implementation Review — workspace-hub issue #2747

You are an independent adversarial code reviewer. Do not rubber-stamp. Review the implementation diff below for issue #2747: raw-to-private-wiki promotion ledger with completion confidence scoring.

## Governance context
- Issue is approved for implementation: status:plan-approved.
- Scope is limited to ledger schema/docs, validator/classifier helper, tests, and implementation notes.
- Acceptance-critical requirements:
  1. ledger includes `source_doc_key`, source/input/output residency, extraction version/provenance, eight confidence dimensions + overall, score metadata, five promotion gates, revision lineage.
  2. validation fails closed on missing/invalid required fields.
  3. public output requires reviewer + legal + sanitization + public release clearance and non-empty rationale.
  4. score is not approval: high score without release clearance must NOT classify as client-ready.
  5. readiness labels: not-started, partial, usable-with-caveats, client-ready, needs-human-review.
  6. revision lineage must preserve prior versions and current lineage version must match extraction.version.
- Tests just run: `uv run pytest tests/client_llm_wiki/test_promotion_ledger.py -q` -> 44 passed.

## Review questions
1. Are there any correctness bugs or acceptance gaps in validation/classification/reporting?
2. Can an entry bypass public/private readiness gates via missing, null, blank, truthy non-boolean, or mismatched fields?
3. Is there any unsafe client-private data handling or public-output leakage risk?
4. Is the documentation/example misleading relative to code behavior?
5. Are tests adequate for the acceptance criteria, or are there missing high-value edge cases?

## Required output format
Verdict: APPROVE | MINOR | MAJOR
Then list findings by severity. MAJOR only for blockers that must be fixed before closing #2747.

## Diffstat
```text
 docs/reports/issue-2747-implementation-notes.html  | 162 ++++++++
 scripts/client_llm_wiki/__init__.py                |   5 +
 scripts/client_llm_wiki/promotion_ledger.py        | 394 ++++++++++++++++++++
 templates/client-llm-wiki/DATA-CYCLE.md            |  11 +-
 templates/client-llm-wiki/ledgers/README.md        |  39 +-
 .../ledgers/promotion-ledger.example.yml           |  40 +-
 tests/client_llm_wiki/__init__.py                  |   0
 tests/client_llm_wiki/test_promotion_ledger.py     | 407 +++++++++++++++++++++
 8 files changed, 1041 insertions(+), 17 deletions(-)

```

## Full diff under review
```diff
diff --git a/docs/reports/issue-2747-implementation-notes.html b/docs/reports/issue-2747-implementation-notes.html
new file mode 100644
index 000000000..0798fbd29
--- /dev/null
+++ b/docs/reports/issue-2747-implementation-notes.html
@@ -0,0 +1,162 @@
+<!DOCTYPE html>
+<html lang="en">
+<head>
+<meta charset="utf-8">
+<title>Issue #2747 — Promotion Ledger Implementation Notes</title>
+<style>
+  body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
+         max-width: 980px; margin: 2rem auto; padding: 0 1.2rem; color: #1a1a1a; line-height: 1.5; }
+  h1, h2, h3 { color: #0b3d91; }
+  h1 { border-bottom: 2px solid #0b3d91; padding-bottom: 0.3rem; }
+  h2 { margin-top: 2rem; border-bottom: 1px solid #ccc; padding-bottom: 0.2rem; }
+  code, pre { font-family: "SFMono-Regular", Menlo, Consolas, monospace; }
+  pre { background: #f5f7fb; padding: 0.8rem 1rem; border-radius: 4px; overflow-x: auto; }
+  code { background: #f0f2f7; padding: 0.05rem 0.3rem; border-radius: 3px; }
+  table { border-collapse: collapse; margin: 1rem 0; }
+  th, td { border: 1px solid #ccc; padding: 0.4rem 0.7rem; text-align: left; vertical-align: top; }
+  th { background: #eef2fb; }
+  .label { display: inline-block; padding: 0.05rem 0.4rem; border-radius: 3px;
+           font-size: 0.85em; background: #eef; color: #024; }
+  .red { color: #a52a2a; }
+  .green { color: #0a6c2a; }
+  .meta { color: #555; font-size: 0.9em; }
+</style>
+</head>
+<body>
+
+<h1>Issue #2747 — Promotion Ledger Implementation Notes</h1>
+<p class="meta">
+  Issue: <a href="https://github.com/vamseeachanta/workspace-hub/issues/2747">#2747</a> ·
+  Plan: <code>docs/plans/2026-05-21-issue-2747-acma-private-wiki-promotion-ledger.md</code> ·
+  Branch: <code>issue-2747-promotion-ledger</code> ·
+  Date: 2026-05-21
+</p>
+
+<h2>Scope delivered</h2>
+<ul>
+  <li>Hardened ledger schema in <code>templates/client-llm-wiki/ledgers/promotion-ledger.example.yml</code> (<code>ledger_version: 0.2</code>).</li>
+  <li>Importable validator and classifier at <code>scripts/client_llm_wiki/promotion_ledger.py</code>.</li>
+  <li>Test suite at <code>tests/client_llm_wiki/test_promotion_ledger.py</code> (44 tests after orchestrator hardening, TDD-driven).</li>
+  <li>README + DATA-CYCLE updates documenting required fields, gates, and the derived readiness classifier.</li>
+</ul>
+
+<h2>Schema fields added beyond the v0.1 example</h2>
+<table>
+  <tr><th>Field</th><th>Why</th></tr>
+  <tr><td><code>source_doc_key</code></td><td>Join key to #2389 doc-intel surface; required by plan §Adversarial Review Hardening.</td></tr>
+  <tr><td><code>input_residency</code> / <code>output_residency</code></td><td>Explicit data-flow residency declaration. Public outputs gated programmatically.</td></tr>
+  <tr><td><code>extraction.version</code></td><td>Anchor for revision lineage; matched against <code>revision_lineage.current_extraction_version</code>.</td></tr>
+  <tr><td><code>score_metadata</code> (scored_by / scored_with / scored_at / rationale_bucket)</td><td>Audit trail for who/what produced the score, not just the score value.</td></tr>
+  <tr><td><code>promotion.gates</code></td><td>Five-clearance gate set: reviewer, legal, sanitization, public release, private release.</td></tr>
+  <tr><td><code>revision_lineage</code></td><td>Preserves prior extraction versions; supersession is explicit, never destructive.</td></tr>
+</table>
+
+<h2>Key design decisions</h2>
+
+<h3>1. Operator <code>overall</code> stays operator-set</h3>
+<p>
+  The plan adversarial review (§58) explicitly requires that derived classification targets a separate report-time
+  surface rather than mutating operator-judgment fields. <code>classify_readiness</code> reads <code>confidence.overall</code>
+  but never writes back to it. The README's "operator judgment, biased toward lowest two sub-fields" convention
+  is preserved verbatim.
+</p>
+
+<h3>2. Score ≠ approval, enforced programmatically</h3>
+<p>
+  A high <code>overall</code> score with no release clearance lands in <code>needs-human-review</code>, never <code>client-ready</code>.
+  This mirrors the workspace-hub must-fire rule <code>feedback_never_offer_to_self_label_plan_approved</code>: the
+  clearance gate is load-bearing and cannot be inferred from telemetry.
+</p>
+
+<h3>3. Single-dimension cap</h3>
+<p>
+  Any confidence sub-field below 0.3 forces <code>needs-human-review</code> regardless of <code>overall</code>. Implements
+  the README's "single weak dimension caps the whole" guidance as a hard ceiling, not advisory copy.
+</p>
+
+<h3>4. Public-output gate enforcement</h3>
+<p>
+  An entry declaring <code>output_residency: public-llm-wiki</code> OR <code>promotion.public_llm_wiki_allowed: true</code>
+  must carry <em>all four</em> public-clearance gates plus a non-empty rationale. Validation fails closed otherwise.
+  This is the programmatic backstop for the <code>DATA-CYCLE.md</code> rule "raw data never moves directly to public llm-wiki".
+</p>
+
+<h3>5. Structural vs semantic validation split</h3>
+<p>
+  <code>validate_structure</code> permits placeholder <code>null</code> values so the shipped example YAML stays a valid
+  schema reference. <code>validate</code> performs the full fail-closed pass for working ledgers. Tests exercise both
+  surfaces: the example YAML against <code>validate_structure</code>, and a fully-populated entry against <code>validate</code>.
+</p>
+
+<h2>Tradeoffs considered</h2>
+<ul>
+  <li>
+    <strong>Thresholds as constants vs config.</strong> Picked module-level constants
+    (<code>READY_OVERALL_MIN = 0.75</code>, etc.) for v0.2. If operators need per-client tuning, this becomes a
+    config knob in a follow-on issue. Not now — premature.
+  </li>
+  <li>
+    <strong>Validation depth.</strong> Did not import <code>jsonschema</code>. The validator is hand-rolled because the
+    rules are small (~150 lines), the error messages are domain-specific (mention <code>source_id</code> and the
+    failing field), and the project already ships custom validators in <code>scripts/</code>. <code>jsonschema</code> is
+    available if a later issue wants formal JSON-Schema generation.
+  </li>
+  <li>
+    <strong>Returning entries by reference vs deep-copying in <code>summarize</code>.</strong> The summary
+    decorates copies with the <code>readiness</code> label so callers can mutate the returned dict without leaking
+    label state back to the source document. Trade: slightly more allocation; gain: no spooky-action.
+  </li>
+</ul>
+
+<h2>Open questions / future work</h2>
+<ul>
+  <li>
+    <strong>#2389 doc-intel join.</strong> Plan dependency calls out <code>source_doc_key</code> consumption from #2389.
+    The validator enforces the field's presence but cannot verify the key exists in the doc-intel surface — that
+    cross-system check belongs in a downstream consumer once #2389 ships, plausibly as a fixture-side check.
+  </li>
+  <li>
+    <strong>#2748 unscored-output prevention.</strong> The plan flags #2748 as blocked-by this work. The natural
+    integration is for #2748 to consume <code>summarize()</code> and refuse to emit any client-facing artifact whose
+    source ledger entry is not in the <code>ready</code> bucket. No code in this PR commits to that integration shape.
+  </li>
+  <li>
+    <strong>CLI surface.</strong> No CLI entry point was added. If operators want a <code>validate-ledger</code>
+    command on PATH, a thin wrapper in <code>scripts/client_llm_wiki/</code> would be a small follow-on.
+  </li>
+  <li>
+    <strong>Threshold calibration.</strong> The 0.3/0.5/0.75 cutoffs are heuristic. A future audit using real
+    ledger data should validate whether <code>usable-with-caveats</code> width is right or wants splitting.
+  </li>
+</ul>
+
+<h2>Tests run</h2>
+
+<h3>RED (before implementation)</h3>
+<pre>$ uv run pytest tests/client_llm_wiki/test_promotion_ledger.py -q
+==================================== ERRORS ====================================
+_______ ERROR collecting tests/client_llm_wiki/test_promotion_ledger.py ________
+ImportError while importing test module
+  '/.../tests/client_llm_wiki/test_promotion_ledger.py'.
+...
+E   ModuleNotFoundError: No module named 'client_llm_wiki'
+=========================== short test summary info ============================
+ERROR tests/client_llm_wiki/test_promotion_ledger.py
+!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!
+1 error in 0.39s</pre>
+<p class="red">RED captured: collection failed because <code>scripts/client_llm_wiki/promotion_ledger.py</code> did not yet exist.</p>
+
+<h3>GREEN (after implementation)</h3>
+<pre>$ uv run pytest tests/client_llm_wiki/test_promotion_ledger.py -q
+............................................                             [100%]
+44 passed in 0.15s</pre>
+<p class="green">GREEN: 44/44 tests pass. Coverage spans validation (structural + fail-closed missing fields, null provenance, blank provenance, null/blank score metadata), gate enforcement (public + private + rationale), score-vs-approval separation, all five threshold labels, single-dimension cap, dashboard groups/counts, and revision lineage preservation.</p>
+
+<h2>Path-contract compliance</h2>
+<ul>
+  <li>All edits live within the prompt's owned-paths allowlist.</li>
+  <li>No <code>/mnt/ace</code> access. No secret material, no <code>.env</code>, no credentials written.</li>
+</ul>
+
+</body>
+</html>
diff --git a/scripts/client_llm_wiki/__init__.py b/scripts/client_llm_wiki/__init__.py
new file mode 100644
index 000000000..b10a21cff
--- /dev/null
+++ b/scripts/client_llm_wiki/__init__.py
@@ -0,0 +1,5 @@
+"""Client llm-wiki promotion-ledger helpers (issue #2747)."""
+
+from . import promotion_ledger
+
+__all__ = ["promotion_ledger"]
diff --git a/scripts/client_llm_wiki/promotion_ledger.py b/scripts/client_llm_wiki/promotion_ledger.py
new file mode 100644
index 000000000..47bc78953
--- /dev/null
+++ b/scripts/client_llm_wiki/promotion_ledger.py
@@ -0,0 +1,394 @@
+"""Promotion-ledger schema validation, readiness classification, and reporting.
+
+Issue: https://github.com/vamseeachanta/workspace-hub/issues/2747
+Plan:  docs/plans/2026-05-21-issue-2747-acma-private-wiki-promotion-ledger.md
+Templates: templates/client-llm-wiki/ledgers/
+
+Design notes:
+- `confidence.overall` is an operator-set field (see ledgers/README.md). The
+  readiness classification returned by ``classify_readiness`` is a DERIVED
+  surface and intentionally separate. This preserves the operator's judgment
+  while letting downstream dashboards/reports compute "scored != approved".
+- Validation is fail-closed: any missing required field, missing residency or
+  provenance, missing score metadata, missing gate state, or missing revision
+  lineage raises ``LedgerValidationError``. Downstream consumers cannot treat
+  the absence of those fields as a benign default.
+- Public output residency requires the full clearance gate set + a non-empty
+  rationale. The DATA-CYCLE.md contract bars raw-to-public flows; this is the
+  programmatic backstop.
+"""
+from __future__ import annotations
+
+from typing import Any, Iterable, Mapping
+
+
+READINESS_LABELS = (
+    "not-started",
+    "partial",
+    "usable-with-caveats",
+    "client-ready",
+    "needs-human-review",
+)
+
+# Confidence dimensions required on every entry (eight + overall).
+CONFIDENCE_DIMENSIONS = (
+    "raw_source_presence",
+    "readability_or_ocr_quality",
+    "extraction_completeness",
+    "metadata_completeness",
+    "citation_quality",
+    "privacy_redaction_classification",
+    "engineering_domain_confidence",
+    "report_readiness",
+)
+
+ALLOWED_SOURCE_CLASSES = {
+    "raw-data",
+    "readable-raw-data",
+    "private-wiki",
+    "public-derivative",
+}
+
+ALLOWED_INPUT_RESIDENCY = {"private-client", "private-internal", "public-eligible"}
+ALLOWED_OUTPUT_RESIDENCY = {"readable-local", "private-wiki", "public-llm-wiki"}
+ALLOWED_RATIONALE_BUCKETS = {
+    "not_started",
+    "mechanical",
+    "model",
+    "human_review",
+    "mixed",
+}
+ALLOWED_PROMOTION_STATUS = {
+    "not_started",
+    "partial",
+    "usable_with_caveats",
+    "client_ready",
+    "needs_human_review",
+}
+
+REQUIRED_GATE_KEYS = (
+    "reviewer_clearance",
+    "legal_clearance",
+    "sanitization_review",
+    "public_release_clearance",
+    "private_release_clearance",
+)
+
+PUBLIC_GATES = (
+    "reviewer_clearance",
+    "legal_clearance",
+    "sanitization_review",
+    "public_release_clearance",
+)
+PRIVATE_GATES = ("reviewer_clearance", "private_release_clearance")
+
+# Classification thresholds — derived only, never written back onto the entry.
+LOW_DIMENSION_CAP = 0.3      # any sub-field below this caps readiness
+PARTIAL_OVERALL_MAX = 0.5    # overall <= this and ungated => partial
+USABLE_OVERALL_MAX = 0.75    # overall in (PARTIAL_OVERALL_MAX, this] and ungated
+READY_OVERALL_MIN = 0.75     # >= this AND all private gates => client-ready
+
+
+class LedgerValidationError(ValueError):
+    """Raised when a ledger document fails fail-closed validation."""
+
+
+# --------------------------------------------------------------------------- #
+# Structural validation                                                       #
+# --------------------------------------------------------------------------- #
+
+
+def validate_structure(doc: Any) -> None:
+    """Shallow structural check used for example/template files.
+
+    Permits placeholder ``null`` values inside entries (the example YAML uses
+    these). Full semantic validation lives in ``validate``.
+    """
+    if not isinstance(doc, Mapping):
+        raise LedgerValidationError("ledger root must be a mapping")
+    for key in ("ledger_version", "client", "entries"):
+        if key not in doc:
+            raise LedgerValidationError(f"ledger missing top-level key '{key}'")
+    if not isinstance(doc["entries"], list):
+        raise LedgerValidationError("ledger 'entries' must be a list")
+    seen_ids: set[str] = set()
+    for idx, entry in enumerate(doc["entries"]):
+        if not isinstance(entry, Mapping):
+            raise LedgerValidationError(f"entry #{idx} must be a mapping")
+        if "source_id" not in entry:
+            raise LedgerValidationError(f"entry #{idx} missing source_id")
+        sid = entry["source_id"]
+        if sid in seen_ids:
+            raise LedgerValidationError(f"duplicate source_id '{sid}'")
+        seen_ids.add(sid)
+
+
+# --------------------------------------------------------------------------- #
+# Full semantic validation                                                    #
+# --------------------------------------------------------------------------- #
+
+
+def validate(doc: Any) -> None:
+    """Fail-closed validation of a ledger document.
+
+    Raises ``LedgerValidationError`` on the first defect encountered.
+    Returns ``None`` on success.
+    """
+    validate_structure(doc)
+    for idx, entry in enumerate(doc["entries"]):
+        _validate_entry(entry, idx)
+
+
+def _require(entry: Mapping, key: str, idx: int, hint: str = "") -> Any:
+    if key not in entry:
+        raise LedgerValidationError(
+            f"entry #{idx} ({entry.get('source_id', '?')}) missing required field '{key}'"
+            + (f" — {hint}" if hint else "")
+        )
+    return entry[key]
+
+
+def _validate_entry(entry: Mapping, idx: int) -> None:
+    sid = entry.get("source_id", "?")
+
+    # Identity + provenance
+    _require(entry, "source_doc_key", idx, "needed for #2389 doc-intel join")
+    _require(entry, "source_path", idx)
+    sc = _require(entry, "source_class", idx)
+    if sc not in ALLOWED_SOURCE_CLASSES:
+        raise LedgerValidationError(
+            f"entry {sid} source_class '{sc}' not in {sorted(ALLOWED_SOURCE_CLASSES)}"
+        )
+
+    input_res = _require(entry, "input_residency", idx)
+    output_res = _require(entry, "output_residency", idx)
+    if input_res not in ALLOWED_INPUT_RESIDENCY:
+        raise LedgerValidationError(
+            f"entry {sid} input_residency '{input_res}' invalid"
+        )
+    if output_res not in ALLOWED_OUTPUT_RESIDENCY:
+        raise LedgerValidationError(
+            f"entry {sid} output_residency '{output_res}' invalid"
+        )
+
+    # Extraction provenance
+    extraction = _require(entry, "extraction", idx)
+    if not isinstance(extraction, Mapping):
+        raise LedgerValidationError(f"entry {sid} extraction must be a mapping")
+    if "version" not in extraction:
+        raise LedgerValidationError(
+            f"entry {sid} extraction.version is required (revision lineage anchor)"
+        )
+    for k in ("method", "tool_version", "extracted_at"):
+        if k not in extraction:
+            raise LedgerValidationError(f"entry {sid} extraction.{k} key missing")
+        _require_nonblank_string(extraction[k], f"entry {sid} extraction.{k}")
+
+    # Confidence (8 + overall)
+    conf = _require(entry, "confidence", idx)
+    if not isinstance(conf, Mapping):
+        raise LedgerValidationError(f"entry {sid} confidence must be a mapping")
+    for dim in CONFIDENCE_DIMENSIONS:
+        if dim not in conf:
+            raise LedgerValidationError(
+                f"entry {sid} confidence.{dim} missing (must be 0.0–1.0)"
+            )
+        _require_unit_float(conf[dim], f"entry {sid} confidence.{dim}")
+    if "overall" not in conf:
+        raise LedgerValidationError(f"entry {sid} confidence.overall missing")
+    _require_unit_float(conf["overall"], f"entry {sid} confidence.overall")
+
+    # Score metadata
+    sm = _require(entry, "score_metadata", idx)
+    if not isinstance(sm, Mapping):
+        raise LedgerValidationError(f"entry {sid} score_metadata must be a mapping")
+    for k in ("scored_by", "scored_with", "scored_at", "rationale_bucket"):
+        if k not in sm:
+            raise LedgerValidationError(f"entry {sid} score_metadata.{k} missing")
+    for k in ("scored_by", "scored_with", "scored_at"):
+        _require_nonblank_string(sm[k], f"entry {sid} score_metadata.{k}")
+    bucket = sm["rationale_bucket"]
+    if bucket not in ALLOWED_RATIONALE_BUCKETS:
+        raise LedgerValidationError(
+            f"entry {sid} score_metadata.rationale_bucket '{bucket}' invalid"
+        )
+
+    # Promotion + gates
+    promotion = _require(entry, "promotion", idx)
+    if not isinstance(promotion, Mapping):
+        raise LedgerValidationError(f"entry {sid} promotion must be a mapping")
+    for k in ("status", "private_wiki_allowed", "public_llm_wiki_allowed",
+              "rationale", "gates"):
+        if k not in promotion:
+            raise LedgerValidationError(f"entry {sid} promotion.{k} missing")
+    status = promotion["status"]
+    if status not in ALLOWED_PROMOTION_STATUS:
+        raise LedgerValidationError(
+            f"entry {sid} promotion.status '{status}' invalid"
+        )
+    gates = promotion["gates"]
+    if not isinstance(gates, Mapping):
+        raise LedgerValidationError(f"entry {sid} promotion.gates must be a mapping")
+    for gk in REQUIRED_GATE_KEYS:
+        if gk not in gates:
+            raise LedgerValidationError(
+                f"entry {sid} promotion.gates.{gk} missing"
+            )
+
+    _enforce_public_output_gates(entry, promotion, output_res, sid)
+
+    # Revision lineage
+    lineage = _require(entry, "revision_lineage", idx)
+    if not isinstance(lineage, Mapping):
+        raise LedgerValidationError(f"entry {sid} revision_lineage must be a mapping")
+    if "current_extraction_version" not in lineage:
+        raise LedgerValidationError(
+            f"entry {sid} revision_lineage.current_extraction_version missing"
+        )
+    if "previous_extraction_versions" not in lineage:
+        raise LedgerValidationError(
+            f"entry {sid} revision_lineage.previous_extraction_versions missing"
+        )
+    if not isinstance(lineage["previous_extraction_versions"], list):
+        raise LedgerValidationError(
+            f"entry {sid} revision_lineage.previous_extraction_versions must be a list"
+        )
+    if lineage["current_extraction_version"] != extraction["version"]:
+        raise LedgerValidationError(
+            f"entry {sid} revision_lineage.current_extraction_version "
+            f"({lineage['current_extraction_version']}) must equal "
+            f"extraction.version ({extraction['version']})"
+        )
+
+
+def _enforce_public_output_gates(
+    entry: Mapping, promotion: Mapping, output_res: str, sid: str
+) -> None:
+    public_declared = (
+        output_res == "public-llm-wiki" or promotion.get("public_llm_wiki_allowed")
+    )
+    if not public_declared:
+        return
+    gates = promotion["gates"]
+    for gk in PUBLIC_GATES:
+        if not gates.get(gk):
+            raise LedgerValidationError(
+                f"entry {sid} declares public output but gate '{gk}' is not cleared"
+            )
+    rationale = promotion.get("rationale") or ""
+    if not rationale.strip():
+        raise LedgerValidationError(
+            f"entry {sid} declares public output but promotion.rationale is empty"
+        )
+
+
+def _require_unit_float(value: Any, label: str) -> None:
+    if not isinstance(value, (int, float)) or isinstance(value, bool):
+        raise LedgerValidationError(f"{label} must be a number")
+    if not (0.0 <= float(value) <= 1.0):
+        raise LedgerValidationError(f"{label} must be in range 0.0–1.0 (got {value})")
+
+
+def _require_nonblank_string(value: Any, label: str) -> None:
+    if not isinstance(value, str) or not value.strip():
+        raise LedgerValidationError(f"{label} must be a non-empty string")
+
+
+# --------------------------------------------------------------------------- #
+# Readiness classification (derived; never mutates the entry)                 #
+# --------------------------------------------------------------------------- #
+
+
+def classify_readiness(entry: Mapping) -> str:
+    """Return one of READINESS_LABELS based on confidence + gate state.
+
+    The classification is intentionally separate from ``promotion.status``.
+    The operator's ``promotion.status`` records their *intent*; this function
+    reports what the ledger *evidences*. They can diverge, and when they do
+    the dashboard exposes the gap.
+    """
+    extraction = entry.get("extraction") or {}
+    not_extracted = (
+        not extraction.get("method")
+        and not extraction.get("tool_version")
+        and not extraction.get("extracted_at")
+    )
+
+    conf = entry.get("confidence") or {}
+    dims = [conf.get(d, 0.0) for d in CONFIDENCE_DIMENSIONS]
+    overall = conf.get("overall", 0.0)
+    has_low_dim = any(float(d) < LOW_DIMENSION_CAP for d in dims)
+
+    promotion = entry.get("promotion") or {}
+    gates = promotion.get("gates") or {}
+    public_cleared = all(gates.get(k) for k in PUBLIC_GATES)
+    private_cleared = all(gates.get(k) for k in PRIVATE_GATES)
+
+    if not_extracted and all(float(d) == 0.0 for d in dims):
+        return "not-started"
+
+    # A single weak dimension caps readiness — operator must remediate or
+    # mark "needs-human-review" explicitly. Mirrors README §"Combining sub-fields".
+    if has_low_dim:
+        return "needs-human-review"
+
+    if private_cleared or public_cleared:
+        if float(overall) >= READY_OVERALL_MIN:
+            return "client-ready"
+        # Cleared but weak score — surface for human review rather than autopromote.
+        return "needs-human-review"
+
+    if float(overall) <= PARTIAL_OVERALL_MAX:
+        return "partial"
+    if float(overall) <= USABLE_OVERALL_MAX:
+        return "usable-with-caveats"
+    # Score is high enough but no clearance recorded — must not slip into
+    # client-ready. The release gate is load-bearing per the plan adversarial
+    # review (`feedback_never_offer_to_self_label_plan_approved` family).
+    return "needs-human-review"
+
+
+# --------------------------------------------------------------------------- #
+# Dashboard / report summary                                                  #
+# --------------------------------------------------------------------------- #
+
+
+def summarize(doc: Mapping) -> dict:
+    """Return a dashboard-shaped summary of a ledger document.
+
+    Shape::
+
+        {
+          "counts": {<label>: int, ...},
+          "ready":  [<entry>, ...],          # only client-ready
+          "blocked":[<entry>, ...],          # everything else (with readiness label attached)
+          "groups": {<label>: [<entry>, ...]},
+        }
+
+    The ``blocked`` list explicitly surfaces low-confidence / partial /
+    needs-human-review items so they cannot be missed before client use.
+    """
+    entries: Iterable[Mapping] = doc.get("entries") or ()
+    counts = {label: 0 for label in READINESS_LABELS}
+    groups: dict[str, list[dict]] = {label: [] for label in READINESS_LABELS}
+
+    for entry in entries:
+        label = classify_readiness(entry)
+        counts[label] += 1
+        decorated = dict(entry)
+        decorated["readiness"] = label
+        groups[label].append(decorated)
+
+    ready = list(groups["client-ready"])
+    blocked: list[dict] = []
+    for label in READINESS_LABELS:
+        if label == "client-ready":
+            continue
+        blocked.extend(groups[label])
+
+    return {
+        "counts": counts,
+        "ready": ready,
+        "blocked": blocked,
+        "groups": groups,
+    }
diff --git a/templates/client-llm-wiki/DATA-CYCLE.md b/templates/client-llm-wiki/DATA-CYCLE.md
index 83d1e655e..0afcc19c5 100644
--- a/templates/client-llm-wiki/DATA-CYCLE.md
+++ b/templates/client-llm-wiki/DATA-CYCLE.md
@@ -46,4 +46,13 @@ Raw data never moves directly to public `llm-wiki`. Promotion path is:
 raw source -> readable derivative -> private <CLIENT_SHORT_NAME> wiki -> reviewed/sanitized derivative -> public llm-wiki, if appropriate
 ```

-Each transition needs a ledger entry.
+Each transition needs a ledger entry. The ledger schema and readiness classifier are defined in `ledgers/README.md` and validated programmatically by `scripts/client_llm_wiki/promotion_ledger.py` (issue #2747).
+
+## Score is not approval
+
+A high confidence score (`confidence.overall ≥ 0.75`) does **not** by itself make an entry client-ready. Promotion to client-facing artifacts requires the explicit release-clearance gates in `promotion.gates`:
+
+- private wiki page: `reviewer_clearance` + `private_release_clearance`
+- public llm-wiki: `reviewer_clearance` + `legal_clearance` + `sanitization_review` + `public_release_clearance` + non-empty rationale
+
+`classify_readiness` enforces this separation: a scored-but-unclearance entry classifies as `needs-human-review`, never `client-ready`. Downstream dashboards, reports, and chatbot retrieval indexes must consume `classify_readiness` (or the equivalent dashboard summary), not raw scores.
diff --git a/templates/client-llm-wiki/ledgers/README.md b/templates/client-llm-wiki/ledgers/README.md
index 29bab41a5..8802144f2 100644
--- a/templates/client-llm-wiki/ledgers/README.md
+++ b/templates/client-llm-wiki/ledgers/README.md
@@ -20,14 +20,19 @@ Ledgers are the audit-trail surface for this private wiki. Every promotion of a
 | `ledger_version` | Schema version. Bump if entries change shape. |
 | `client` | Short client identifier (matches `<CLIENT_SHORT_NAME>`). |
 | `entries[].source_id` | Stable identifier for the source. Convention: `<CLIENT_SHORT_NAME_UPPER>-SOURCE-NNNN`. |
+| `entries[].source_doc_key` | Stable doc-intel key (shared with #2389). Required for cross-system join. |
 | `entries[].source_path` | Absolute path under `/mnt/ace/<CLIENT_RAW_ROOT>/`. |
 | `entries[].source_class` | One of: `raw-data`, `readable-raw-data`, `private-wiki`, `public-derivative`. |
+| `entries[].input_residency` | One of: `private-client`, `private-internal`, `public-eligible`. |
+| `entries[].output_residency` | One of: `readable-local`, `private-wiki`, `public-llm-wiki`. |
 | `entries[].readable_derivative_path` | Path to OCR/text/markdown extract. `null` if not yet produced. |
 | `entries[].private_wiki_page` | Path to the curated page under `pages/`. `null` if not yet promoted. |
-| `entries[].extraction` | How the readable derivative was produced (method, tool version, timestamp). |
-| `entries[].confidence` | Per-dimension confidence scores 0.0–1.0; see "Confidence sub-fields" below. |
-| `entries[].promotion` | Promotion gate state: status, private/public allowances, rationale. |
-| `entries[].revision_trigger` | When to revisit (e.g., when better OCR models exist). |
+| `entries[].extraction` | How the readable derivative was produced (`version`, `method`, `tool_version`, `extracted_at`). |
+| `entries[].confidence` | Per-dimension confidence scores 0.0–1.0 plus operator-set `overall`; see "Confidence sub-fields" below. |
+| `entries[].score_metadata` | Who/what produced the score (`scored_by`, `scored_with`, `scored_at`, `rationale_bucket`). |
+| `entries[].promotion` | Promotion gate state: `status`, private/public allowances, rationale, `gates`. |
+| `entries[].promotion.gates` | `reviewer_clearance`, `legal_clearance`, `sanitization_review`, `public_release_clearance`, `private_release_clearance`. |
+| `entries[].revision_lineage` | `current_extraction_version`, `previous_extraction_versions[]`, `supersedes`, `superseded_by`, `revision_trigger`. |

 ## Confidence sub-fields

@@ -54,14 +59,34 @@ The `confidence` block records eight per-dimension scores (range 0.0–1.0) plus

 The point is operator judgment, not arithmetic — the sub-fields exist so the rationale is inspectable.

+## Readiness classification (derived)
+
+`scripts/client_llm_wiki/promotion_ledger.py` exposes `classify_readiness(entry)`, which returns one of five labels independent of the operator's `promotion.status`:
+
+| Label | Condition |
+|---|---|
+| `not-started` | No extraction recorded and all confidence sub-fields are 0.0. |
+| `partial` | `overall ≤ 0.5` and no release clearance gate is set. |
+| `usable-with-caveats` | `overall` in `(0.5, 0.75]` and no release clearance gate is set. |
+| `client-ready` | `overall ≥ 0.75` AND all private-release gates cleared (`reviewer_clearance` + `private_release_clearance`). |
+| `needs-human-review` | Any single sub-field below 0.3 (caps), OR a release gate cleared but `overall < 0.75`, OR `overall ≥ 0.75` with no clearance recorded. |
+
+**Score is not approval.** A score above 0.75 with no clearance lands in `needs-human-review`, not `client-ready`. Dashboards/reports must use `classify_readiness`, never raw `confidence.overall`, when deciding whether knowledge is client-usable.
+
 ## Validation

 Every ledger file must:

 - be valid YAML (parses without error)
 - have `ledger_version`, `client`, and `entries` at the root
-- have every entry carry a unique `source_id`
-- have `promotion.public_llm_wiki_allowed: true` ONLY when a sanitization review is recorded in `promotion.rationale` and `REDACTION-POSTURE.md` defaults have been applied
+- have every entry carry a unique `source_id` plus `source_doc_key`
+- declare `source_class`, `input_residency`, `output_residency`
+- carry full `extraction` provenance (`version`, `method`, `tool_version`, `extracted_at`)
+- carry all eight confidence sub-fields plus `overall`
+- carry `score_metadata` (actor, tool, timestamp, rationale bucket)
+- carry `promotion.gates` with all five gate keys present
+- have `promotion.public_llm_wiki_allowed: true` (or `output_residency: public-llm-wiki`) ONLY when sanitization review, legal clearance, reviewer clearance, and public release clearance are recorded with a non-empty rationale
+- carry `revision_lineage` with `current_extraction_version` matching `extraction.version` and a `previous_extraction_versions` list (may be empty)
 - never carry credentials, raw-extract bodies, or client-private bulk content — ledgers point to artifacts, they don't embed them

-A ledger that violates these rules is invalid and must be corrected before further entries are appended.
+A ledger that violates these rules is invalid and must be corrected before further entries are appended. Programmatic validation is performed by `scripts/client_llm_wiki/promotion_ledger.py::validate()` and fails closed on the first defect.
diff --git a/templates/client-llm-wiki/ledgers/promotion-ledger.example.yml b/templates/client-llm-wiki/ledgers/promotion-ledger.example.yml
index 643d29ea8..49d12e797 100644
--- a/templates/client-llm-wiki/ledgers/promotion-ledger.example.yml
+++ b/templates/client-llm-wiki/ledgers/promotion-ledger.example.yml
@@ -1,16 +1,22 @@
 # Example only. Copy to a dated ledger file before use.
-ledger_version: 0.1
+# Schema reference for issue #2747 promotion ledger with completion confidence scoring.
+ledger_version: 0.2
 client: <CLIENT_SHORT_NAME>
 entries:
   - source_id: <CLIENT_SHORT_NAME_UPPER>-SOURCE-0001
+    # source_doc_key is the stable identifier shared with #2389 doc-intel surface.
+    source_doc_key: <CLIENT_SHORT_NAME_UPPER>-DOC-0001
     source_path: /mnt/ace/<CLIENT_RAW_ROOT>/<project>/<source-file>
-    source_class: raw-data
+    source_class: raw-data                      # raw-data | readable-raw-data | private-wiki | public-derivative
+    input_residency: private-client             # private-client | private-internal | public-eligible
+    output_residency: private-wiki              # readable-local | private-wiki | public-llm-wiki
     readable_derivative_path: null
     private_wiki_page: null
     extraction:
-      method: null
+      version: 0                                # bumps with each AI-model revision; preserved in revision_lineage
+      method: null                              # e.g. pdftotext, pymupdf, tesseract, docling
       tool_version: null
-      extracted_at: null
+      extracted_at: null                        # ISO-8601 UTC
     confidence:
       raw_source_presence: 0.0
       readability_or_ocr_quality: 0.0
@@ -20,12 +26,28 @@ entries:
       privacy_redaction_classification: 0.0
       engineering_domain_confidence: 0.0
       report_readiness: 0.0
-      overall: 0.0
+      overall: 0.0                              # operator-set per README guidance; NOT the readiness classifier
+    score_metadata:
+      scored_by: null                           # actor that emitted the score (human handle, model id, automation)
+      scored_with: null                         # tool/model + version used to score
+      scored_at: null                           # ISO-8601 UTC
+      rationale_bucket: not_started             # not_started | mechanical | model | human_review | mixed
     promotion:
-      status: not_started
+      status: not_started                       # not_started | partial | usable_with_caveats | client_ready | needs_human_review
       private_wiki_allowed: false
       public_llm_wiki_allowed: false
       rationale: "Initial placeholder; not reviewed."
-    revision_trigger:
-      revisit_when_models_improve: true
-      notes: null
+      gates:
+        reviewer_clearance: false               # operator/SME signed off content
+        legal_clearance: false                  # legal/compliance signed off
+        sanitization_review: false              # REDACT/FLAG-FOR-REVIEW pass applied
+        public_release_clearance: false         # explicit "ok for public llm-wiki" gate
+        private_release_clearance: false        # explicit "ok for private wiki" gate
+    revision_lineage:
+      current_extraction_version: 0
+      previous_extraction_versions: []          # list of prior extraction snapshots; never destructive
+      supersedes: null                          # source_id this entry supersedes, if any
+      superseded_by: null                       # source_id that supersedes this entry, if any
+      revision_trigger:
+        revisit_when_models_improve: true
+        notes: null
diff --git a/tests/client_llm_wiki/__init__.py b/tests/client_llm_wiki/__init__.py
new file mode 100644
index 000000000..e69de29bb
diff --git a/tests/client_llm_wiki/test_promotion_ledger.py b/tests/client_llm_wiki/test_promotion_ledger.py
new file mode 100644
index 000000000..78a6753c4
--- /dev/null
+++ b/tests/client_llm_wiki/test_promotion_ledger.py
@@ -0,0 +1,407 @@
+"""Tests for the ACMA private-wiki promotion ledger (issue #2747).
+
+The tests exercise:
+- schema/field validation (fail-closed)
+- readiness classification (5 labels)
+- "scored != approved" gate separation
+- public-output gate enforcement
+- dashboard/report summary
+- revision lineage preservation
+"""
+from __future__ import annotations
+
+import copy
+from pathlib import Path
+
+import pytest
+import yaml
+
+from client_llm_wiki import promotion_ledger as pl
+
+
+REPO_ROOT = Path(__file__).resolve().parents[2]
+EXAMPLE_YAML = (
+    REPO_ROOT
+    / "templates"
+    / "client-llm-wiki"
+    / "ledgers"
+    / "promotion-ledger.example.yml"
+)
+
+
+def _base_entry() -> dict:
+    """A clean, fully-scored, private-wiki-cleared entry. Tests mutate copies."""
+    return {
+        "source_id": "ACME-SOURCE-0001",
+        "source_doc_key": "ACME-DOC-0001",
+        "source_path": "/mnt/ace/acme/projectX/report.pdf",
+        "source_class": "readable-raw-data",
+        "input_residency": "private-client",
+        "output_residency": "private-wiki",
+        "readable_derivative_path": "derivatives/acme/projectX/report.md",
+        "private_wiki_page": "pages/acme/projectX/report.md",
+        "extraction": {
+            "version": 2,
+            "method": "pymupdf",
+            "tool_version": "1.24.0",
+            "extracted_at": "2026-05-21T10:15:00Z",
+        },
+        "confidence": {
+            "raw_source_presence": 0.95,
+            "readability_or_ocr_quality": 0.85,
+            "extraction_completeness": 0.80,
+            "metadata_completeness": 0.75,
+            "citation_quality": 0.80,
+            "privacy_redaction_classification": 0.90,
+            "engineering_domain_confidence": 0.85,
+            "report_readiness": 0.80,
+            "overall": 0.82,
+        },
+        "score_metadata": {
+            "scored_by": "human:vamsee",
+            "scored_with": "manual-review:v1",
+            "scored_at": "2026-05-21T11:00:00Z",
+            "rationale_bucket": "human_review",
+        },
+        "promotion": {
+            "status": "client_ready",
+            "private_wiki_allowed": True,
+            "public_llm_wiki_allowed": False,
+            "rationale": "Reviewer + legal signed off on private wiki page.",
+            "gates": {
+                "reviewer_clearance": True,
+                "legal_clearance": True,
+                "sanitization_review": False,
+                "public_release_clearance": False,
+                "private_release_clearance": True,
+            },
+        },
+        "revision_lineage": {
+            "current_extraction_version": 2,
+            "previous_extraction_versions": [
+                {"version": 1, "extracted_at": "2026-04-01T10:00:00Z", "method": "pdftotext"},
+                {"version": 0, "extracted_at": "2026-03-01T10:00:00Z", "method": "pdftotext"},
+            ],
+            "supersedes": None,
+            "superseded_by": None,
+            "revision_trigger": {
+                "revisit_when_models_improve": True,
+                "notes": "Re-extract when next OCR rev lands.",
+            },
+        },
+    }
+
+
+def _base_ledger(entries=None) -> dict:
+    return {
+        "ledger_version": 0.2,
+        "client": "ACME",
+        "entries": entries if entries is not None else [_base_entry()],
+    }
+
+
+# ---------- example YAML --------------------------------------------------- #
+
+
+def test_example_yaml_parses_and_is_structurally_valid():
+    """The shipped example YAML must parse and pass structural validation
+    (placeholder values are allowed; the example is a schema reference)."""
+    data = yaml.safe_load(EXAMPLE_YAML.read_text())
+    # Structural validation only — the example uses placeholder values that
+    # would not pass strict semantic validation (e.g. nulls for extraction).
+    pl.validate_structure(data)
+
+
+def test_validate_passes_for_fully_populated_entry():
+    pl.validate(_base_ledger())
+
+
+# ---------- fail-closed missing field tests -------------------------------- #
+
+
+@pytest.mark.parametrize(
+    "missing_path",
+    [
+        ("source_doc_key",),
+        ("source_class",),
+        ("input_residency",),
+        ("output_residency",),
+        ("extraction", "version"),
+        ("score_metadata",),
+        ("score_metadata", "scored_by"),
+        ("score_metadata", "scored_at"),
+        ("score_metadata", "rationale_bucket"),
+        ("promotion", "gates"),
+        ("promotion", "gates", "reviewer_clearance"),
+        ("revision_lineage",),
+        ("revision_lineage", "current_extraction_version"),
+        ("revision_lineage", "previous_extraction_versions"),
+    ],
+)
+def test_validate_fails_closed_on_missing_required_field(missing_path):
+    entry = _base_entry()
+    cursor = entry
+    for key in missing_path[:-1]:
+        cursor = cursor[key]
+    del cursor[missing_path[-1]]
+    with pytest.raises(pl.LedgerValidationError):
+        pl.validate(_base_ledger([entry]))
+
+
+def test_validate_fails_closed_on_missing_confidence_dimension():
+    entry = _base_entry()
+    del entry["confidence"]["report_readiness"]
+    with pytest.raises(pl.LedgerValidationError):
+        pl.validate(_base_ledger([entry]))
+
+
+def test_validate_fails_closed_on_missing_overall_confidence():
+    entry = _base_entry()
+    del entry["confidence"]["overall"]
+    with pytest.raises(pl.LedgerValidationError):
+        pl.validate(_base_ledger([entry]))
+
+
+@pytest.mark.parametrize(
+    "path_to_null",
+    [
+        ("extraction", "method"),
+        ("extraction", "tool_version"),
+        ("extraction", "extracted_at"),
+        ("score_metadata", "scored_by"),
+        ("score_metadata", "scored_with"),
+        ("score_metadata", "scored_at"),
+    ],
+)
+def test_validate_fails_closed_on_null_provenance_or_score_metadata(path_to_null):
+    entry = _base_entry()
+    cursor = entry
+    for key in path_to_null[:-1]:
+        cursor = cursor[key]
+    cursor[path_to_null[-1]] = None
+    with pytest.raises(pl.LedgerValidationError):
+        pl.validate(_base_ledger([entry]))
+
+
+@pytest.mark.parametrize(
+    "path_to_blank",
+    [
+        ("extraction", "method"),
+        ("extraction", "tool_version"),
+        ("extraction", "extracted_at"),
+        ("score_metadata", "scored_by"),
+        ("score_metadata", "scored_with"),
+        ("score_metadata", "scored_at"),
+    ],
+)
+def test_validate_fails_closed_on_blank_provenance_or_score_metadata(path_to_blank):
+    entry = _base_entry()
+    cursor = entry
+    for key in path_to_blank[:-1]:
+        cursor = cursor[key]
+    cursor[path_to_blank[-1]] = "   "
+    with pytest.raises(pl.LedgerValidationError):
+        pl.validate(_base_ledger([entry]))
+
+
+# ---------- gate / approval enforcement ------------------------------------ #
+
+
+def test_public_output_requires_all_clearance_gates():
+    """An entry declaring public output must carry sanitization + legal +
+    reviewer + public_release_clearance + rationale. Missing any => fail."""
+    entry = _base_entry()
+    entry["output_residency"] = "public-llm-wiki"
+    entry["promotion"]["public_llm_wiki_allowed"] = True
+    # All gates default to "missing"; only private gates were set in base.
+    with pytest.raises(pl.LedgerValidationError):
+        pl.validate(_base_ledger([entry]))
+
+
+def test_public_output_accepted_when_all_gates_present():
+    entry = _base_entry()
+    entry["output_residency"] = "public-llm-wiki"
+    entry["promotion"]["public_llm_wiki_allowed"] = True
+    entry["promotion"]["rationale"] = (
+        "Sanitization REDACT pass complete; FLAG-FOR-REVIEW signed off; "
+        "legal cleared; reviewer cleared; public release approved."
+    )
+    entry["promotion"]["gates"] = {
+        "reviewer_clearance": True,
+        "legal_clearance": True,
+        "sanitization_review": True,
+        "public_release_clearance": True,
+        "private_release_clearance": True,
+    }
+    pl.validate(_base_ledger([entry]))
+
+
+def test_public_allowance_requires_nonempty_rationale():
+    entry = _base_entry()
+    entry["output_residency"] = "public-llm-wiki"
+    entry["promotion"]["public_llm_wiki_allowed"] = True
+    entry["promotion"]["rationale"] = ""
+    entry["promotion"]["gates"] = {
+        "reviewer_clearance": True,
+        "legal_clearance": True,
+        "sanitization_review": True,
+        "public_release_clearance": True,
+        "private_release_clearance": True,
+    }
+    with pytest.raises(pl.LedgerValidationError):
+        pl.validate(_base_ledger([entry]))
+
+
+# ---------- scored-but-not-approved separation ----------------------------- #
+
+
+def test_high_score_alone_is_not_client_ready():
+    """An entry can have excellent confidence yet lack any release clearance.
+    classify_readiness must return needs_human_review, not client_ready."""
+    entry = _base_entry()
+    entry["promotion"]["private_wiki_allowed"] = False
+    entry["promotion"]["gates"]["reviewer_clearance"] = False
+    entry["promotion"]["gates"]["private_release_clearance"] = False
+    entry["promotion"]["status"] = "client_ready"  # operator may have over-claimed
+    assert pl.classify_readiness(entry) == "needs-human-review"
+
+
+# ---------- threshold classification --------------------------------------- #
+
+
+def test_classify_not_started_when_extraction_absent():
+    entry = _base_entry()
+    entry["extraction"]["method"] = None
+    entry["extraction"]["tool_version"] = None
+    entry["extraction"]["extracted_at"] = None
+    entry["extraction"]["version"] = 0
+    for k in entry["confidence"]:
+        entry["confidence"][k] = 0.0
+    entry["score_metadata"]["rationale_bucket"] = "not_started"
+    entry["promotion"]["status"] = "not_started"
+    entry["promotion"]["private_wiki_allowed"] = False
+    entry["promotion"]["gates"]["reviewer_clearance"] = False
+    entry["promotion"]["gates"]["legal_clearance"] = False
+    entry["promotion"]["gates"]["private_release_clearance"] = False
+    assert pl.classify_readiness(entry) == "not-started"
+
+
+def test_classify_partial_when_low_overall_and_no_clearance():
+    entry = _base_entry()
+    for k in entry["confidence"]:
+        entry["confidence"][k] = 0.4
+    entry["confidence"]["overall"] = 0.4
+    entry["promotion"]["private_wiki_allowed"] = False
+    entry["promotion"]["gates"]["reviewer_clearance"] = False
+    entry["promotion"]["gates"]["legal_clearance"] = False
+    entry["promotion"]["gates"]["private_release_clearance"] = False
+    assert pl.classify_readiness(entry) == "partial"
+
+
+def test_classify_usable_with_caveats_when_mid_score_no_clearance():
+    entry = _base_entry()
+    for k in entry["confidence"]:
+        entry["confidence"][k] = 0.65
+    entry["confidence"]["overall"] = 0.65
+    entry["promotion"]["private_wiki_allowed"] = False
+    entry["promotion"]["gates"]["reviewer_clearance"] = False
+    entry["promotion"]["gates"]["legal_clearance"] = False
+    entry["promotion"]["gates"]["private_release_clearance"] = False
+    assert pl.classify_readiness(entry) == "usable-with-caveats"
+
+
+def test_classify_client_ready_when_high_score_and_clearance():
+    entry = _base_entry()  # already client-ready scoring + private clearance
+    assert pl.classify_readiness(entry) == "client-ready"
+
+
+def test_classify_needs_human_review_when_high_score_but_low_privacy_dimension():
+    """A single weak privacy/redaction confidence dimension must block
+    client-ready regardless of overall score (caps logic per README)."""
+    entry = _base_entry()
+    entry["confidence"]["privacy_redaction_classification"] = 0.2
+    assert pl.classify_readiness(entry) == "needs-human-review"
+
+
+# ---------- dashboard / summary -------------------------------------------- #
+
+
+def test_summarize_groups_entries_by_readiness():
+    not_started = _base_entry()
+    not_started["source_id"] = "ACME-SOURCE-0002"
+    not_started["extraction"]["method"] = None
+    not_started["extraction"]["tool_version"] = None
+    not_started["extraction"]["extracted_at"] = None
+    not_started["extraction"]["version"] = 0
+    for k in not_started["confidence"]:
+        not_started["confidence"][k] = 0.0
+    not_started["score_metadata"]["rationale_bucket"] = "not_started"
+    not_started["promotion"]["status"] = "not_started"
+    not_started["promotion"]["private_wiki_allowed"] = False
+    not_started["promotion"]["gates"] = {
+        "reviewer_clearance": False,
+        "legal_clearance": False,
+        "sanitization_review": False,
+        "public_release_clearance": False,
+        "private_release_clearance": False,
+    }
+
+    partial = copy.deepcopy(not_started)
+    partial["source_id"] = "ACME-SOURCE-0003"
+    for k in partial["confidence"]:
+        partial["confidence"][k] = 0.4
+    partial["confidence"]["overall"] = 0.4
+    partial["extraction"]["method"] = "pdftotext"
+    partial["extraction"]["tool_version"] = "4.04"
+    partial["extraction"]["extracted_at"] = "2026-05-10T00:00:00Z"
+    partial["extraction"]["version"] = 1
+
+    ready = _base_entry()  # ACME-SOURCE-0001 client-ready
+    summary = pl.summarize(_base_ledger([not_started, partial, ready]))
+
+    assert summary["counts"]["not-started"] == 1
+    assert summary["counts"]["partial"] == 1
+    assert summary["counts"]["client-ready"] == 1
+    assert summary["counts"]["usable-with-caveats"] == 0
+    assert summary["counts"]["needs-human-review"] == 0
+
+    ready_ids = {e["source_id"] for e in summary["ready"]}
+    blocked_ids = {e["source_id"] for e in summary["blocked"]}
+    assert ready_ids == {"ACME-SOURCE-0001"}
+    assert blocked_ids == {"ACME-SOURCE-0002", "ACME-SOURCE-0003"}
+
+
+def test_summarize_surfaces_low_confidence_items():
+    weak = _base_entry()
+    weak["source_id"] = "ACME-SOURCE-0010"
+    weak["confidence"]["privacy_redaction_classification"] = 0.1
+    summary = pl.summarize(_base_ledger([weak]))
+    # Low-confidence dimension must downgrade the entry out of ready set.
+    assert summary["counts"]["needs-human-review"] == 1
+    assert any(e["source_id"] == "ACME-SOURCE-0010" for e in summary["blocked"])
+
+
+# ---------- revision lineage ----------------------------------------------- #
+
+
+def test_revision_lineage_preserves_prior_versions():
+    entry = _base_entry()
+    assert entry["revision_lineage"]["current_extraction_version"] == 2
+    prior_versions = [
+        p["version"] for p in entry["revision_lineage"]["previous_extraction_versions"]
+    ]
+    assert prior_versions == [1, 0]
+
+
+def test_revision_lineage_current_version_must_match_extraction_version():
+    entry = _base_entry()
+    entry["revision_lineage"]["current_extraction_version"] = 1  # mismatched
+    with pytest.raises(pl.LedgerValidationError):
+        pl.validate(_base_ledger([entry]))
+
+
+def test_revision_lineage_previous_versions_must_be_list():
+    entry = _base_entry()
+    entry["revision_lineage"]["previous_extraction_versions"] = None
+    with pytest.raises(pl.LedgerValidationError):
+        pl.validate(_base_ledger([entry]))

```

warning: Codex's Linux sandbox uses bubblewrap and needs access to create user namespaces.
hook: SessionStart
hook: SessionStart
hook: SessionStart
hook: SessionStart Completed
hook: SessionStart Completed
hook: SessionStart Completed
hook: UserPromptSubmit
hook: UserPromptSubmit Completed
codex
Using `adversarial-code-review-and-fix` as the closest workflow fit: this is an adversarial implementation review, and I’m applying it in review-only mode because you supplied the full diff and required verdict format.
hook: PreToolUse
hook: PreToolUse
hook: PreToolUse
hook: PreToolUse
hook: PreToolUse
hook: PreToolUse Completed
hook: PreToolUse Completed
hook: PreToolUse Completed
hook: PreToolUse Completed
hook: PreToolUse Completed
hook: PostToolUse
hook: PostToolUse
hook: PostToolUse
hook: PostToolUse Completed
hook: PostToolUse Completed
hook: PostToolUse Completed
codex
Verdict: MAJOR

Findings by severity:

MAJOR: Gate fields are truthiness-checked, not boolean-validated.
`scripts/client_llm_wiki/promotion_ledger.py` only checks that `promotion.gates.*` keys exist, then uses `gates.get(...)` in `_enforce_public_output_gates()` and `classify_readiness()`. Values like `"yes"`, `"false"`, `1`, `[]`/`{}` variants can change validation/classification behavior by Python truthiness. A public entry with string gate values can pass public clearance, and a private entry with truthy non-booleans can classify as `client-ready`. This directly violates the fail-closed and “truthy non-boolean” acceptance concern. Add strict `isinstance(value, bool)` validation for all five gates and for `private_wiki_allowed` / `public_llm_wiki_allowed`.

MAJOR: Required identity/provenance fields allow null/blank values.
`source_doc_key`, `source_path`, and `extraction.version` are only checked for key presence. `source_doc_key: null`, `source_doc_key: "   "`, `source_path: ""`, or `extraction.version: null` can pass if lineage matches. That undercuts required provenance, doc-intel joinability, and revision lineage anchoring. `extraction.version` should be a non-null scalar with a defined type policy, and source identifiers/paths should be nonblank strings.

MAJOR: Public/private readiness can be inferred from gates even when allowance booleans are false or invalid.
`classify_readiness()` ignores `promotion.private_wiki_allowed` and `promotion.public_llm_wiki_allowed` for readiness and relies only on gates. That may be intentional for “evidenced readiness,” but the docs describe explicit release-clearance/allowance state. At minimum, validation should reject contradictory states such as `private_wiki_allowed: true` without private gates, public output with non-boolean allowances, and possibly cleared gates with allowance false if allowance is intended to be authoritative. As written, the meaning of the allowance fields is misleading and easy for downstream consumers to misuse.

MINOR: Revision lineage preservation is only shallowly validated.
The validator checks that `previous_extraction_versions` is a list and that `current_extraction_version == extraction.version`, but does not validate prior-version item shape, ordering, uniqueness, or that prior versions are actually prior. If “preserve prior versions” is acceptance-critical, add tests for malformed previous entries and duplicate/current-version leakage.

MINOR: `summarize()`/`classify_readiness()` do not fail closed on unvalidated input.
They default missing structures to `{}` / `0.0` and may raise raw `ValueError` on bad numeric strings. If these are intended downstream reporting APIs, consider making `summarize(validate_first=True)` or documenting that callers must run `validate()` first. Current behavior is mostly conservative, but not explicitly fail-closed.

Test gaps:
Add high-value tests for non-boolean gates/allowances, blank/null `source_doc_key`, blank `source_path`, null/mismatched `extraction.version`, public gates set to strings, private readiness with string gates, and contradictory `*_allowed` fields versus gates. These are the main bypass paths not covered by the 44 passing tests.
hook: Stop
hook: Stop
hook: Stop
hook: Stop
hook: Stop
hook: Stop Completed
hook: Stop Completed
hook: Stop Failed
hook: Stop Completed
hook: Stop Completed
tokens used
54,971
Verdict: MAJOR

Findings by severity:

MAJOR: Gate fields are truthiness-checked, not boolean-validated.
`scripts/client_llm_wiki/promotion_ledger.py` only checks that `promotion.gates.*` keys exist, then uses `gates.get(...)` in `_enforce_public_output_gates()` and `classify_readiness()`. Values like `"yes"`, `"false"`, `1`, `[]`/`{}` variants can change validation/classification behavior by Python truthiness. A public entry with string gate values can pass public clearance, and a private entry with truthy non-booleans can classify as `client-ready`. This directly violates the fail-closed and “truthy non-boolean” acceptance concern. Add strict `isinstance(value, bool)` validation for all five gates and for `private_wiki_allowed` / `public_llm_wiki_allowed`.

MAJOR: Required identity/provenance fields allow null/blank values.
`source_doc_key`, `source_path`, and `extraction.version` are only checked for key presence. `source_doc_key: null`, `source_doc_key: "   "`, `source_path: ""`, or `extraction.version: null` can pass if lineage matches. That undercuts required provenance, doc-intel joinability, and revision lineage anchoring. `extraction.version` should be a non-null scalar with a defined type policy, and source identifiers/paths should be nonblank strings.

MAJOR: Public/private readiness can be inferred from gates even when allowance booleans are false or invalid.
`classify_readiness()` ignores `promotion.private_wiki_allowed` and `promotion.public_llm_wiki_allowed` for readiness and relies only on gates. That may be intentional for “evidenced readiness,” but the docs describe explicit release-clearance/allowance state. At minimum, validation should reject contradictory states such as `private_wiki_allowed: true` without private gates, public output with non-boolean allowances, and possibly cleared gates with allowance false if allowance is intended to be authoritative. As written, the meaning of the allowance fields is misleading and easy for downstream consumers to misuse.

MINOR: Revision lineage preservation is only shallowly validated.
The validator checks that `previous_extraction_versions` is a list and that `current_extraction_version == extraction.version`, but does not validate prior-version item shape, ordering, uniqueness, or that prior versions are actually prior. If “preserve prior versions” is acceptance-critical, add tests for malformed previous entries and duplicate/current-version leakage.

MINOR: `summarize()`/`classify_readiness()` do not fail closed on unvalidated input.
They default missing structures to `{}` / `0.0` and may raise raw `ValueError` on bad numeric strings. If these are intended downstream reporting APIs, consider making `summarize(validate_first=True)` or documenting that callers must run `validate()` first. Current behavior is mostly conservative, but not explicitly fail-closed.

Test gaps:
Add high-value tests for non-boolean gates/allowances, blank/null `source_doc_key`, blank `source_path`, null/mismatched `extraction.version`, public gates set to strings, private readiness with string gates, and contradictory `*_allowed` fields versus gates. These are the main bypass paths not covered by the 44 passing tests.
