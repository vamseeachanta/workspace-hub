"""
Generate a minimal OrcaFlex .sim fixture for integration testing.

Creates a model with: vessel + 1 mooring line + environment, 10s simulation.
Output: digitalmodel/tests/fixtures/minimal_test.sim (target < 1 MB)
"""
import os
import sys
import OrcFxAPI

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FIXTURE_DIR = os.path.join(REPO_ROOT, "digitalmodel", "tests", "fixtures")
os.makedirs(FIXTURE_DIR, exist_ok=True)

SIM_PATH = os.path.join(FIXTURE_DIR, "minimal_test.sim")
DAT_PATH = os.path.join(FIXTURE_DIR, "minimal_test.dat")

print("Creating minimal OrcaFlex model...")
model = OrcFxAPI.Model()

# --- Environment ---
env = model.environment
env.WaterDepth = 100.0

# --- General: short simulation (statics only + 10s dynamic) ---
general = model.general
general.StageDuration[0] = 5.0   # build-up stage
general.StageDuration[1] = 10.0  # simulation stage

# --- Vessel ---
vessel = model.CreateObject(OrcFxAPI.ObjectType.Vessel, "TestVessel")
vessel.InitialX = 0.0
vessel.InitialY = 0.0
vessel.InitialZ = 0.0
vessel.InitialHeading = 0.0

# --- Line type (required for line creation) ---
line_type = model.CreateObject(OrcFxAPI.ObjectType.LineType, "Chain")
line_type.OD = 0.1
line_type.ID = 0.0
line_type.MassPerUnitLength = 100.0  # kg/m
line_type.EA = 854e6  # N (stiffness)

# --- Mooring line ---
line = model.CreateObject(OrcFxAPI.ObjectType.Line, "MooringLine1")
line.EndAConnection = "TestVessel"
line.EndAX = 25.0
line.EndAY = 0.0
line.EndAZ = -5.0
line.EndBConnection = "Anchored"
line.EndBX = 200.0
line.EndBY = 0.0
line.EndBHeightAboveSeabed = 0.0
line.Length[0] = 250.0
line.LineType[0] = "Chain"
line.TargetSegmentLength[0] = 25.0  # 10 segments over 250m

# --- Run statics ---
print("Running statics...")
model.CalculateStatics()
print("  Statics complete")

# --- Run dynamics ---
print("Running dynamics (10s)...")
model.RunSimulation()
print("  Dynamics complete")

# --- Save ---
model.SaveSimulation(SIM_PATH)
print(f"Saved .sim: {SIM_PATH}")

model.SaveData(DAT_PATH)
print(f"Saved .dat: {DAT_PATH}")

# --- File size check ---
sim_size_mb = os.path.getsize(SIM_PATH) / 1e6
print(f"File size: {sim_size_mb:.2f} MB")
if sim_size_mb > 1.0:
    print("WARNING: File exceeds 1 MB target — consider reducing simulation duration")
else:
    print("File size OK (< 1 MB)")

# --- Verify load ---
print("Verifying fixture loads correctly...")
verify = OrcFxAPI.Model(SIM_PATH)
obj_names = [obj.name for obj in verify.objects]
print(f"  Object count: {len(obj_names)}")
print(f"  Objects: {obj_names[:10]}")
print("Done.")
