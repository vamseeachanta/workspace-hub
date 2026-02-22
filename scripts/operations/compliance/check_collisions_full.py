from pathlib import Path
import sys
collisions = []
collisions_fold = []
type_conflicts = []
for p in Path("worldenergydata").rglob("*"):
    s = str(p).replace("\\", "/")
    if p.is_file() and "/specs/" in s:
        t = s.replace("worldenergydata/", "specs/repos/worldenergydata/", 1)
        tp = Path(t)
        if tp.exists():
            collisions.append(f"{s} -> {t}")
            if tp.is_dir():
                type_conflicts.append(f"file->dir conflict: {s} -> {t}")
        # parent path collision: file exists where directory is needed
        parent = tp.parent
        while str(parent).startswith("specs/repos/worldenergydata") and str(parent) != "specs/repos/worldenergydata":
            if parent.exists() and parent.is_file():
                type_conflicts.append(f"dir->file conflict: {s} -> parent {parent}")
                break
            parent = parent.parent
        # Case-insensitive collision check for cross-platform safety
        if not tp.exists():
            parent = tp.parent
            if parent.exists():
                name_fold = tp.name.lower()
                for sibling in parent.iterdir():
                    if sibling.name.lower() == name_fold:
                        collisions_fold.append(f"{s} -> {sibling} (case-fold)")
Path("reports/compliance/wrk-188-worldenergydata-target-collisions.txt").write_text("\n".join(collisions))
Path("reports/compliance/wrk-188-worldenergydata-target-collisions-casefold.txt").write_text("\n".join(collisions_fold))
Path("reports/compliance/wrk-188-worldenergydata-target-type-conflicts.txt").write_text("\n".join(type_conflicts))
if collisions or collisions_fold or type_conflicts:
    print(f"Collisions: {len(collisions)}, Casefold: {len(collisions_fold)}, Type conflicts: {len(type_conflicts)}")
    sys.exit(1)
