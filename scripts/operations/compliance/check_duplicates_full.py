from pathlib import Path
import sys
targets = []
for p in Path("worldenergydata").rglob("*"):
    s = str(p).replace("\\","/")
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
nl = chr(10)
Path("reports/compliance/wrk-188-worldenergydata-duplicate-targets.txt").write_text(nl.join(sorted(dups)) + nl)
Path("reports/compliance/wrk-188-worldenergydata-duplicate-targets-casefold.txt").write_text(nl.join(sorted(dups_fold)) + nl)
if dups or dups_fold:
    print(f"Duplicates: {len(dups)}, Casefold duplicates: {len(dups_fold)}")
    sys.exit(1)
