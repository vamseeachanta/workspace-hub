# WRK-642 Claude No-Response Test Results

## Matrix

| Case | Input Shape | Prompt Shape | Invocation | Timeout | Exit | Classification | Evidence |
|---|---|---|---|---:|---:|---|---|
| C1 | minimal schema target | strict reviewer | direct `claude -p` | 30s | 0 | `VALID` | `raw/c1/stdout.md` |
| C2 | compact WRK-624 bundle | strict reviewer | direct `claude -p` | 30s | 124 | `NO_OUTPUT` | `raw/c2/` |
| C3 | compact WRK-624 bundle | baseline wrapper JSON prompt | `submit-to-claude.sh` | 30s | 0 | `NO_OUTPUT` wrapper fallback | `raw/c3/stdout.md` |
| C4 | full WRK-624 plan | strict reviewer | direct `claude -p` | 30s | 1 | harness error | `raw/c4/stderr.md` |
| C5 | full WRK-624 plan | baseline wrapper JSON prompt | `submit-to-claude.sh` | 30s | 0 | `NO_OUTPUT` wrapper fallback | `raw/c5/stdout.md` |
| C6 | compact WRK-624 bundle | strict reviewer JSON prompt | `submit-to-claude.sh` | 60s | 137 | wrapper hang / leaked process chain | `raw/c6/stdout.md` |

## Notes by Case

### C1
- Control case passed.
- Claude can produce schema-compliant non-interactive review output when payload size and task complexity are minimal.

### C2
- Same strict prompt path fails on the compact WRK-624 review bundle.
- No stdout or stderr was produced before timeout.

### C3
- Wrapper completed, but only by returning its own fallback stub.
- The provider call underneath did not produce renderable structured output.

### C4
- This case does not measure provider quality.
- It exposed a command construction defect: the full markdown payload was passed positionally and parsed as CLI options.

### C5
- Full plan through wrapper also degraded to wrapper fallback.
- This aligns with the hypothesis that larger review payloads are the main trigger, independent of direct vs wrapper path.

### C6
- The wrapper path remained alive after its internal 60-second timeout budget.
- The process chain had to be terminated manually.
- This indicates a transport cleanup defect in addition to the provider no-output behavior.
