from pathlib import Path
import sys

collisions = []
for p in Path("worldenergydata").rglob("*"):
    s = str(p).replace("\\", "/")
    if p.is_file() and "/specs/" in s:
        t = s.replace("worldenergydata/", "specs/repos/worldenergydata/", 1)
        if Path(t).exists():
            collisions.append(f"{s} -> {t}")

report_path = Path("reports/compliance/wrk-188-worldenergydata-target-collisions.txt")
report_path.parent.mkdir(parents=True, exist_ok=True)
report_path.write_text("\n".join(collisions))

if collisions:
    print(f"Found {len(collisions)} collisions")
    sys.exit(1)
sys.exit(0)
