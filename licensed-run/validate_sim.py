"""Validate that a candidate .sim is a genuine, solved OrcaFlex simulation
with a Line carrying the strength-post result variables.

Usage:  uv run python validate_sim.py <path-to-.sim>
Prints VALIDATE: PASS or VALIDATE: FAIL with reasons. Read-only on the .sim.
"""
import sys

path = sys.argv[1] if len(sys.argv) > 1 else None
if not path:
    print("VALIDATE: FAIL  (no .sim path given)")
    raise SystemExit(2)

try:
    import OrcFxAPI
except Exception as exc:  # license / install / VPN
    print(f"VALIDATE: FAIL  import OrcFxAPI failed: {type(exc).__name__}: {exc}")
    raise SystemExit(1)

print(f"OrcFxAPI import: ok  (DLL version {OrcFxAPI.DLLVersion()})")

try:
    model = OrcFxAPI.Model(path)
except Exception as exc:
    print(f"VALIDATE: FAIL  could not load .sim: {type(exc).__name__}: {exc}")
    raise SystemExit(1)

state = model.state
print(f"model.state: {state}")

solved_states = {
    getattr(OrcFxAPI.ModelState, n, object())
    for n in ("SimulationStopped", "SimulationStoppedUnstable", "SimulationPaused")
}
is_solved = state in solved_states

lines = [o for o in model.objects if getattr(o, "typeName", "") == "Line"]
print(f"Line objects: {[o.name for o in lines]}")

ok = is_solved and bool(lines)
reason = []
if not is_solved:
    reason.append(f"state {state} is not a completed simulation")
if not lines:
    reason.append("no Line object present")

sample = {}
if lines:
    line = lines[0]
    period = OrcFxAPI.Period(OrcFxAPI.pnWholeSimulation) if is_solved else OrcFxAPI.Period(OrcFxAPI.pnStaticState)
    for var in ("Effective Tension", "Wall Tension", "Bend Moment", "Curvature", "Bend Radius"):
        try:
            rg = line.RangeGraph(var, period)
            mx = max(rg.Max)
            mn = min(rg.Min)
            sample[var] = (round(mn, 4), round(mx, 4))
        except Exception as exc:
            sample[var] = f"ERR {type(exc).__name__}: {exc}"
    print("range-graph sample (min over Min, max over Max):")
    for k, v in sample.items():
        print(f"   {k:18s} {v}")
    if any(isinstance(v, str) for v in sample.values()):
        ok = False
        reason.append("one or more strength variables not retrievable")

print("VALIDATE: PASS" if ok else "VALIDATE: FAIL  (" + "; ".join(reason) + ")")
raise SystemExit(0 if ok else 1)
