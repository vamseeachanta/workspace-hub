from pathlib import Path
collisions = []
collisions_fold = []
for p in Path("worldenergydata").rglob("*"):
    s = str(p).replace("\\", "/")
    if p.is_file() and "/specs/" in s:
        t = s.replace("worldenergydata/", "specs/repos/worldenergydata/", 1)
        if Path(t).exists():
            collisions.append(f"{s} -> {t}")
        # Case-insensitive collision check for cross-platform safety
        tp = Path(t)
        if not tp.exists():
            parent = tp.parent
            if parent.exists():
                name_fold = tp.name.lower()
                for sibling in parent.iterdir():
                    if sibling.name.lower() == name_fold:
                        collisions_fold.append(f"{s} -> {sibling} (case-fold)")
Path("reports/compliance/wrk-188-worldenergydata-target-collisions.txt").write_text("\n".join(collisions))
Path("reports/compliance/wrk-188-worldenergydata-target-collisions-casefold.txt").write_text("\n".join(collisions_fold))
if collisions or collisions_fold:
    print(f"Collisions found: {collisions}")
    print(f"Case-fold collisions found: {collisions_fold}")
    exit(1)
