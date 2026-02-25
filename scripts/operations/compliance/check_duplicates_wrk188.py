from pathlib import Path
targets = []
for p in Path("worldenergydata").rglob("*"):
    if p.is_file() and "/specs/" in str(p).replace("\\","/"):
        targets.append(str(p).replace("worldenergydata/", "specs/repos/worldenergydata/", 1))
seen = set()
dups = set()
seen_fold = {}
dups_fold = set()
for t in targets:
    if t in seen:
        dups.add(t)
    tf = t.lower()
    if tf in seen_fold and seen_fold[tf] != t:
        dups_fold.add(f"{seen_fold[tf]} <<->> {t}")
    else:
        seen_fold[tf] = t
    seen.add(t)
Path("reports/compliance/wrk-188-worldenergydata-duplicate-targets.txt").write_text("\n".join(sorted(dups)))
Path("reports/compliance/wrk-188-worldenergydata-duplicate-targets-casefold.txt").write_text("\n".join(sorted(dups_fold)))
if dups or dups_fold:
    print(f"Duplicates found: {dups}")
    print(f"Case-fold duplicates found: {dups_fold}")
    exit(1)
