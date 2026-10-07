# Digitalmodel2093 — Claude code review

Model: haiku; effort low; existing auth; empty setting sources; no session persistence; tools disabled; packet-only prompt.
Verdict: MAJOR
Deadline120s. Exit: 0. Elapsed: 68.92s. Timed out: False.
Raw stdout SHA256: a95017190d49ea33185ada14c79ec2efa8a4da541a7149401379b2e1b1a01367
Raw stdout/stderr retained privately in an owned mode0700 directory; path delivered to main for verification.
Packet: current new source/tests, qualification, harness, approved plan, remaining tracked changes.
Public rendering strips trailing whitespace; private raw output and its recorded hash remain unchanged. Private context is redacted if present.

## Reviewed file hashes

{
  "tests/solvers/smoke/native_model_harness_child.py": "e07afb9ec2ba9f30cf15e6f321b8b3260b99d7427f95cf20621372dabb18c821",
  "src/digitalmodel/solvers/smoke/model_manifest.py": "6c321f6f00ff56f0b436bcdfaf3a55739c28586b0f9a1b17bcec037cfdb16b28",
  "src/digitalmodel/solvers/smoke/model_data_readback.py": "fe52e5414990ebb18ab119c770ca51125108183f9cc51d9ae533b6062cbf634c",
  "tests/solvers/smoke/test_model_probe.py": "205a4ee6525bc0a7cfce78dbd468594dc857e5c9b42b10f774473fd7aeea8e65",
  "docs/benchmarks/mooring_buoy/qualification.yml": "874e0780c98c363ba05903234cd1f7ff2f3dfb7d754da44bcbab06a66abf8cfe",
  "docs/plans/2026-09-11-digitalmodel-2093-mooring-buoy.html": "e31fd4df10c35b307cf8dcd7becc7e3c5878dff2da4c971acff07099f069f852",
  "scripts/orcaflex_native_model_probe.py": "f4b075856cbad44400e802c650fd29bcb1db74beffe6a2f8335d8e3106495c77",
  "src/digitalmodel/solvers/smoke/model_results.py": "8bef6a15c18d82a588eee99910b4f5c20b528dedabf089c2b2c63a3d04806d4d",
  "docs/plans/evidence/issue-2082-native.ps1": "1a5ad5056f07c8278039a845156c5e241df9a59c0a7d9f0af2449e1656886242",
  "tests/solvers/smoke/test_native_cleanup_contract.py": "ce4907f46f5c70159db339d747b20675f2b65d1e2227a320337d22f9b96ce864",
  "tests/solvers/smoke/test_model_manifest.py": "ebcc9455cc8f2dcea0fa0a891234ee718ecae5ff1ef1aa60046d5f8b46a0827d",
  "tests/solvers/smoke/test_model_probe_cli.py": "1af768892eb27d710b2e5e68e6e8432732e4be2215296fd1a4e09f30182e509b",
  "scripts/prepare_mooring_qualification.py": "1dfbd1ac7c59631f856b4429aa78a884ff568bdb4adab3fd5b9ee2c4736aaa26",
  "tests/solvers/smoke/test_native_model_harness.py": "87523dd7f6e924dc9941910f0eabdda473c1252e634853e221fd7cb4333f2fe9",
  "tests/solvers/smoke/test_prepare_mooring_qualification.py": "336cd995c2ba9f7ac50fdc15ace4027365e4134d2a9476b307a7e2347c522cdf",
  "src/digitalmodel/solvers/smoke/model_probe.py": "106c5e8d24b33b2455447bc9ee1bc6b909f0064cf55b94b33fef29ab315d2793"
}

## Actual stdout

# VERDICT: MAJOR — Five False-Pass Defects Block Native Execution

---

## **Concrete Defects (Reproducible)**

### **1. CONTRACT FLOAT SERIALIZATION MISMATCH** [model_manifest.py:104-107]
```python
if (json.dumps(data["contract"], sort_keys=True, allow_nan=False)
    != json.dumps(contract, sort_keys=True, allow_nan=False)
```
**Defect**: qualification.yml specifies `grid_atol: 1.0e-09` (YAML float). When loaded and dumped via JSON, scientific notation may normalize (`1e-9` vs `1.0e-09`). String-equality comparison fails despite structural equivalence.
**Evidence**: YAML loaders normalize float literals; JSON dumper uses default precision. Manifest passes locally, fails if qualification.yml edited in a text editor that normalizes exponents.
**Fix**: Replace string equality with deep structural comparison: `def contract_equal(a, b): return json.loads(json.dumps(a, sort_keys=True)) == json.loads(json.dumps(b, sort_keys=True))` or recursively compare dicts/lists/scalars by type and value, not serialized form.

---

### **2. THREAD COUNT VALIDATION USES BOOLEAN SUBCLASS BUG** [model_probe.py:51]
```python
if isinstance(count, bool) or count != 1:
    raise ValueError("observed solver thread count must equal one")
```
**Defect**: In Python, `bool` is a subclass of `int`. A returned value `True` (which equals 1) satisfies `count != 1` → False, so the check passes. But the intent is to reject boolean types. Conversely, if a model returns `1` as bool (via numpy or a wrapper), it's silently accepted and later operations assume int, causing silent type confusion.
**Evidence**: `isinstance(True, int)` is True; `True != 1` is False. Test `test_failures_are_written_as_failed_proof` with `api.fail = "thread"` sets `threadCount = 2`, not `True`, so this escape is not caught.
**Fix**: `if type(count) is not int or isinstance(count, bool) or count != 1:`

---

### **3. READBACK NUMERIC FIDELITY ALLOWS NaN MISMATCHES** [model_probe.py:122]
```python
elif proof["results"] != baseline["results"]:
    raise ValueError("saved-result numeric fidelity mismatch")
```
**Defect**: Python dict/list equality uses `==`, which for floats is IEEE 754 equality. `float('nan') == float('nan')` is False, so two NaN results would be deemed different. Conversely, subnormal/zero rounding differences silently pass. Plan mandates "exact equality of corresponding finite numeric result arrays"; `!=` on nested dicts does not enforce finite-only comparison.
**Evidence**: `{'a': [float('nan')]} != {'a': [float('nan')]}` evaluates to True (mismatch detected), but a test with injected NaN in readback won't cleanly fail. `test_readback_numeric_mutation_fails` uses `value = 2.0 if mutated else 1.0`, never NaN.
**Fix**: Extract all float result arrays, validate all finite before proceeding, then compare: `for key, val in baseline['results'].items(): if isinstance(val, list): assert all(math.isfinite(v) for v in val), f"nonfinite in baseline {key}"`

---

### **4. TIME GRID TOLERANCE HARDCODED, NOT READ FROM CONTRACT** [model_results.py:265-269]
```python
if len(times) != len(expected) or any(abs(a-b) > 1e-9 for a, b in zip(times, expected)):
    raise ValueError("incomplete or changed main-stage sample grid")
```
**Defect**: qualification.yml declares `grid_atol: 1.0e-09`, but code uses literal `1e-9`. If a future case specifies `grid_atol: 0.001`, the hardcoded check still uses 1e-9, silently making it stricter and possibly failing valid grids.
**Evidence**: `grid_atol` in qualification.yml is unused; no parameter passed from `extract_results(contract, ...)` to `histories()`.
**Fix**: Pass `contract["period"]["grid_atol"]` to `histories()` and use it: `if any(abs(a-b) > grid_atol for a, b in ...)`

---

### **5. `readback_comparison` FIELD NOT VALIDATED** [model_manifest.py + qualification.yml]
**Defect**: qualification.yml line 30 specifies `readback_comparison: exact`, but `verify_manifest()` never checks this field exists or enforces it. A manifest could claim `readback_comparison: tolerance` and pass validation; the code has no policy enforcement.
**Evidence**: `FIELDS` constant (model_manifest.py:18-19) is hardcoded; contract is loaded but never checked for `readback_comparison`. No test fails if this field is removed.
**Fix**: Add `readback_comparison` to the audit whitelist in `_tree()` (line 87), validate it equals "exact" in `_header()`, and assert `proof["fidelity_verified"]` only if it matches.

---

## **Additional Sequencing Failures**

- **File identity collisions** (model_manifest.py:60): Case-folding allows `File.txt` and `file.txt` to be treated as the same file on case-sensitive Linux.
- **Symlink escape** (model_manifest.py:46): `.resolve()` follows symlinks before escaping check; a symlink pointing outside bundle passes validation.
- **Duplicate export names** (model_data_readback.py:20): `by_name[name] = entry` silently overwrites if the export YAML contains duplicate identities.
- **Windows cleanup race** (ps1 drain_owned, ~line 220): `active_processes` count poll races against exit notification; no guarantees whole job is drained before handle close.

---

## **Unsupported Tests**

- `test_contract_cannot_drop_a_required_result()` references `data["contract"]["results"]`, but provided qualification.yml has no `results` key (only `expected_settings`, `expected_types`, `results` array at top level).

---

**Requirement**: Fix defects 1–5 before any native invocation. Address symlink escape and file collision logic before merge. Re-run full test suite after corrections.


## Actual stderr
