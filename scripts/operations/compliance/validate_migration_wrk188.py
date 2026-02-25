from pathlib import Path
import sys

# Collision check
collisions = []
for p in Path("worldenergydata").rglob("*"):
    s = str(p).replace("\\", "/")
    if p.is_file() and "/specs/" in s:
        t = s.replace("worldenergydata/", "specs/repos/worldenergydata/", 1)
        if Path(t).exists():
            collisions.append(f"{s} -> {t}")
Path("reports/compliance/wrk-188-worldenergydata-target-collisions.txt").write_text("\n".join(collisions))

# Duplicate target check
targets = []
for p in Path("worldenergydata").rglob("*"):
    s = str(p).replace("\\", "/")
    if p.is_file() and "/specs/" in s:
        targets.append(s.replace("worldenergydata/", "specs/repos/worldenergydata/", 1))

seen = set()
dups = set()
seen_fold = {}
dups_fold = set()
for t in targets:
    if t in seen:
        dups.add(t)
    tf = t.lower()
    if tf in seen_fold and seen_fold[tf] != t:
        dups_fold.add(f"{seen_fold[tf]} <-> {t}")
    else:
        seen_fold[tf] = t
    seen.add(t)
Path("reports/compliance/wrk-188-worldenergydata-duplicate-targets.txt").write_text("\n".join(sorted(dups)))
Path("reports/compliance/wrk-188-worldenergydata-duplicate-targets-casefold.txt").write_text("\n".join(sorted(dups_fold)))

if collisions or dups or dups_fold:
    print(f"Collisions: {len(collisions)}, Dups: {len(dups)}, Casefold Dups: {len(dups_fold)}")
    sys.exit(1)
print("No collisions or duplicates found.")
