"""Produce a real licensed strength_loadcase.sim for the acma strength-post run.

Loads an Orcina example riser model (a Line with bending stiffness), runs a real
OrcaFlex statics + short dynamic solve, and saves the .sim straight to the scope
path the workflow reads. Then reloads and reports a sanity sample.

Usage:
  uv run python build_strength_sim.py [source.dat] [target.sim]
"""
import os
import sys

SRC = sys.argv[1] if len(sys.argv) > 1 else (
    r"C:\ws\digitalmodel\docs\domains\orcaflex\examples\raw\A01\A01 Catenary riser.dat"
)
DST = sys.argv[2] if len(sys.argv) > 2 else (
    r"C:\ws\llm-wiki-acma\cases\orcaflex-strength-post\strength_loadcase.sim"
)

import OrcFxAPI
print(f"OrcFxAPI {OrcFxAPI.DLLVersion()}  (license seat acquired on import)")

print(f"load model: {SRC}")
model = OrcFxAPI.Model(SRC)

lines = [o for o in model.objects if getattr(o, "typeName", "") == "Line"]
print(f"Line objects in source: {[o.name for o in lines]}")
if not lines:
    print("BUILD: FAIL  source model has no Line — pick a different source .dat")
    raise SystemExit(1)

try:
    model.general.StageDuration = [8.0, 12.0]
    print(f"StageDuration set to {list(model.general.StageDuration)}")
except Exception as exc:
    print(f"(left default StageDuration; could not override: {type(exc).__name__}: {exc})")

print("CalculateStatics() ...")
model.CalculateStatics()
print("RunSimulation() ...")
model.RunSimulation()
print(f"post-run state: {model.state}")

os.makedirs(os.path.dirname(DST), exist_ok=True)
model.SaveSimulation(DST)
size_mb = os.path.getsize(DST) / (1024 * 1024)
print(f"SAVED: {DST}  ({size_mb:.2f} MB)")

check = OrcFxAPI.Model(DST)
line = [o for o in check.objects if getattr(o, "typeName", "") == "Line"][0]
period = OrcFxAPI.Period(OrcFxAPI.pnWholeSimulation)
print(f"sanity sample on Line '{line.name}' (range-graph min..max over simulation):")
for var in ("Effective Tension", "Wall Tension", "Bend Moment", "Curvature", "Bend Radius"):
    try:
        rg = line.RangeGraph(var, period)
        print(f"   {var:18s} {min(rg.Min):.4g} .. {max(rg.Max):.4g}")
    except Exception as exc:
        print(f"   {var:18s} (n/a: {type(exc).__name__}: {exc})")
print("BUILD: OK")
