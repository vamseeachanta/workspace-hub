from pathlib import Path
import sys

targets = []
for p in Path("worldenergydata").rglob("*"):
    s = str(p).replace("\\", "/")
    if p.is_file() and "/specs/" in s:
        targets.append(s.replace("worldenergydata/", "specs/repos/worldenergydata/", 1))

seen = set()
dups = set()
for t in targets:
    if t in seen:
        dups.add(t)
    seen.add(t)

report_path = Path("reports/compliance/wrk-188-worldenergydata-duplicate-targets.txt")
report_path.parent.mkdir(parents=True, exist_ok=True)
report_path.write_text(chr(10).join(sorted(dups)))

if dups:
    print(f"Found {len(dups)} duplicate targets")
    sys.exit(1)
sys.exit(0)
