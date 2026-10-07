# Digitalmodel2093 — Claude plan review

Model: haiku; effort low; existing auth; empty setting sources; no session persistence; tools disabled; packet-only prompt.
Verdict: MAJOR
Deadline120s. Exit: 0. Elapsed: 89.96s. Timed out: False.
Private temporary directory removed: True.
Raw stdout SHA256: 43803364b74541ef123d7141c2c07d8d6af563baf97ceb744e8ede67d3f639f9
Packet: exact plan/readiness report, mooring spec, general builder and existing local harness.
Private context redacted if present; trailing line whitespace normalized for repository checks. Wording and raw-output hash are preserved.

## Reviewed file hashes

{
  "src/digitalmodel/solvers/orcaflex/modular_generator/builders/general_builder.py": "3a7a19499103320f25886fb4c83f8cf2f01ad05191388757f3ef9bfef6d4d1b3",
  "docs/plans/evidence/issue-2082-native.ps1": "78c357b4745fa7292bad1aad68ad2ab1c175929eb177ffb8ee845396fc775fff",
  "docs/plans/2026-09-11-digitalmodel-2093-mooring-buoy.html": "27a2c45e2660c151a52f5298db2a9df86851446f44fa12a522ec0ba2e830df6e",
  "docs/domains/orcaflex/library/templates/mooring_buoy/spec.yml": "970db50284209181104fe65c97d6aaae89668975c8b99e57506cab3fea2acede",
  "docs/reports/2026-09-11-orcaflex-mooring-readiness.html": "339d5c59d486f7d797c87305fa717b8451beb431db05993f2a15a8aad9d71332"
}

## Actual stdout

# ADVERSARIAL REVIEW — Mooring-Buoy End-to-End Plan (2093)

**VERDICT: MAJOR**

The plan establishes sound operational governance (immutable inputs, bounded cleanup, explicit fidelity gates) but contains **six material defects** that will block reproducible implementation and acceptance verification. Approval is conditional on resolving these specification gaps before code begins.

---

## Material Defects

### 1. **Serialization Repair Undefined** ⚠ CRITICAL
**Problem:**
Readiness report identifies `RestartStateRecordingTest: ~` (YAML null) as the risky generated value. Plan says "field-specific repair will emit the intended empty script default" but does NOT specify what that is.

Current builder code:
```python
"RestartStateRecordingTest": None,  # Python None
```

Serializes to `RestartStateRecordingTest: ~` in YAML, which previously caused native failure.

**Must clarify before implementation:**
- Is correct value an empty string `""`?
- A different YAML null representation?
- A boolean `false`?
- An entirely omitted field?

The TDD regression cannot be written until this is defined. Acceptance cannot verify correctness.

---

### 2. **Harness Design Ambiguity**
**Problem:**
Plan says "reuse… existing local bounded harness" (issue-2082-native.ps1) but ALSO says "An explicit model mode will preserve fixed-smoke mode." The existing script invokes `solver_smoke_test.py --solver orcaflex`, a **fixed test with known outputs**. New proposal requires arbitrary model loading via modular generator.

**Are you:**
- Extending the existing script to accept `--model-spec case-036/spec.yml`?
- Writing a new wrapper?
- Patching solver_smoke_test.py?

**Defect:**
Without design, the implementation will guess. The review scope (plan approval vs. harness design approval) is unclear. If a new harness is required, its design must be approved alongside this plan.

---

### 3. **Fidelity Tolerance Not Predeclared**
**Problem:**
Plan states: "Exact equality will be used where supported; otherwise a representation-based tolerance documented before comparison will be required."

This is a **forward-looking statement**, not a predeclaration. Plan will extract:
- Tension (kN)
- Positions (m, m, m)
- Angles (°)
- Sea-surface height (m)

**Evidence script only validates:**
- Finiteness (not equality)
- Sample count (exact)

**Defect:**
What tolerance governs pass/fail?
- ±0.5%? ±0.01%? Bit-identical?
- Unit round-trip preserved?
- Single-precision → reload → single-precision exact?

If tolerance is unspecified, independent readback "verification" becomes subjective. Define tolerances NOW for each extracted quantity, or evidence script cannot validate.

---

### 4. **Output Selection Completeness Undefined**
**Problem:**
Plan says probe will extract "Mooring End A/End B effective tensions, static line positions and buoy position, plus buoy X/Z/pitch and sea-surface Z histories… Unsupported selections… will fail the stage."

**Which are REQUIRED vs. OPTIONAL?**
- If buoy has no history output, does it fail the stage or skip that output?
- If sea-surface Z is not in environment, fail or skip?
- Minimum viable subset?

**Defect:**
Probe design cannot proceed without explicit cardinality. Acceptance cannot be verified. The artifact map says probe will "reject unsupported selections" but doesn't define what "supported" means.

---

### 5. **Observed Solve Duration Not Cited**
**Problem:**
Plan specifies 300-second wall-clock timeout for the entire solve (load → verify → statics → dynamics → extract → save). Spec defines 11.5 + 100 simulated seconds, but **wall-clock time is unknown**.

Readiness report measured offline validation only (no solver invocation), so no real duration exists.

**Defect:**
If a realistic solve takes 280 seconds and the limit is 300 seconds, there is no margin for license acquisition delay or OS contention. Is 300s informed by measured timing, or a guess? Cite observed or estimated wall-clock duration with justification before approval.

---

### 6. **Manifest Format Not Defined**
**Problem:**
Plan promises "case evidence manifest" as a deliverable, described as: "enumerate the master and every include, reject escaping/changed paths, unsupported external dependencies and execution hooks."

Artifact map lists:
```
New docs/benchmarks/mooring_buoy/qualification.yml
```

Is this the manifest? If so:
- Is it YAML schema (what keys)?
- JSON (what structure)?
- Plain-text checklist?
- Machine-readable or human-only?

**Defect:**
Without format, implementation will invent one. Acceptance cannot verify it covers "every include" if structure is undefined. Specify schema and required fields before code.

---

## Secondary Gaps (Non-Blocking, But Clarify)

**Offline difference manifest timing unclear:**
Plan says "An offline difference manifest will precede any paired solve" but doesn't say whether this is created *before* Attempt 1 or *before* Attempt 2. Does a material mismatch in the manifest consume one of the two bounded attempts?

**Readback equality verification code missing:**
Evidence script checks `dynamic_samples != reloaded_dynamic_samples` (exact match) but provides no mechanism to compare actual force/position values. Is this intentional (sample count proof only) or an implementation oversight?

**Bundle immutability enforcement absent:**
Plan says "fixed Python hash seed" but harness doesn't show `PYTHONHASHSEED=` being set or verified. Specify enforcement in harness before execution.

**C07 reference damping divergence:**
Readiness report flags "fluid-relative damping in guide versus Earth-relative damping in YAML." Plan says expose it in report, but doesn't clarify: is C07 a true numerical oracle, or just a "known working" comparison point? If the two are intentionally different, state why.

---

## Strengths

✓ **Honest gap ownership**: Plan explicitly states physical qualification is deferred; no invented percentage or success flag claimed.
✓ **Failure preservation**: "Preserve exact failing include/object and stop; do not retune coefficients to force success."
✓ **Bounded attempts**: Two full solves max; third requires new checkpoint.
✓ **Cleanup rigor**: Job Object with kill-on-close, process deadline, orphan detection.

---

## Approval Condition

**Revise plan to:**
1. Specify exact `RestartStateRecordingTest` correct value (string/bool/omitted).
2. Design the harness (extend existing, or new wrapper?). Clarify scope.
3. Predefine fidelity tolerances for each of six output quantities.
4. Enumerate REQUIRED vs. optional probe outputs.
5. Cite observed or justified wall-clock solve time ≤ 300 seconds.
6. Define manifest YAML/JSON schema and required fields.
7. Clarify offline-manifest → attempt sequencing.
8. Document PYTHONHASHSEED enforcement in harness code section.

**Do not start implementation until these are resolved in writing.** Adversarial code review and readback tests will then be straightforward; acceptance criteria will be verifiable.

---

**Word count: 597**


## Actual stderr
