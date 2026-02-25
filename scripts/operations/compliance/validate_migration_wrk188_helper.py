from pathlib import Path
roots = set()
src_files = []
tgt_files = []
bad_paths = []
for p in Path("worldenergydata").rglob("*"):
    s = str(p).replace("\\", "/")
    if p.is_file() and "/specs/" in s:
        if any(ord(ch) < 32 for ch in s):
            bad_paths.append(s)
        src_files.append(s)
        tgt_files.append(s.replace("worldenergydata/", "specs/repos/worldenergydata/", 1))
        roots.add(s.split("/specs/", 1)[0] + "/specs")
Path("reports/compliance/wrk-188-worldenergydata-source-spec-roots.txt").write_text("\n".join(sorted(roots)) + "\n")
Path("reports/compliance/wrk-188-worldenergydata-approved-source-files.txt").write_text("\n".join(sorted(src_files)) + "\n")
Path("reports/compliance/wrk-188-worldenergydata-approved-target-files.txt").write_text("\n".join(sorted(tgt_files)) + "\n")
Path("reports/compliance/wrk-188-worldenergydata-invalid-paths.txt").write_text("\n".join(sorted(bad_paths)))
if bad_paths:
    print(f"Bad paths found: {bad_paths}")
    exit(1)
