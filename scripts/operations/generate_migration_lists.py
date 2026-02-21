from pathlib import Path
roots = set()
src_files = []
tgt_files = []
for p in Path("worldenergydata").rglob("*"):
    s = str(p).replace("", "/")
    if p.is_file() and "/specs/" in s:
        src_files.append(s)
        tgt_files.append(s.replace("worldenergydata/", "specs/repos/worldenergydata/", 1))
        roots.add(s.split("/specs/", 1)[0] + "/specs")
Path("reports/compliance/wrk-188-worldenergydata-source-spec-roots.txt").write_text("
".join(sorted(roots)) + "
")
Path("reports/compliance/wrk-188-worldenergydata-approved-source-files.txt").write_text("
".join(sorted(src_files)) + "
")
Path("reports/compliance/wrk-188-worldenergydata-approved-target-files.txt").write_text("
".join(sorted(tgt_files)) + "
")
