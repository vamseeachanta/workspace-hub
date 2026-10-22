"""Read-only index mode audit; output JSON or a Markdown table.

Mode source: Git 2.44.0 git-ls-files --stage and git-update-index --chmod.
Only indexed regular files are audited; links and submodules are not scripts.
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path, PurePosixPath


def git_env():
    """Do not let a caller's repository binding redirect the requested audit."""
    return {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}


def git(repo, *args, allowed=(0,)):
    result = subprocess.run(
        ["git", "-C", str(repo), *args], env=git_env(), capture_output=True, check=False,
    )
    if result.returncode not in allowed:
        raise ValueError("Git index could not be read")
    return result.stdout


def audit(repo):
    """Use indexed blobs, not working-tree permissions or unstaged content."""
    candidates = set(git(
        repo, "grep", "--cached", "-a", "-l", "-z", "^#!", "--", allowed=(0, 1),
    ).split(b"\0"))
    records = []
    for entry in git(repo, "ls-files", "--stage", "-z").split(b"\0"):
        if not entry:
            continue
        metadata, path = entry.split(b"\t", 1)
        mode, oid, stage = metadata.split()
        if stage != b"0":
            raise ValueError("Unmerged index entries cannot be audited")
        if mode not in (b"100644", b"100755"):
            continue
        if mode == b"100644" and path not in candidates:
            continue
        # The candidate scan avoids reading non-script blobs a second time.
        shebang = git(repo, "cat-file", "blob", oid.decode()).startswith(b"#!")
        kind = None
        if shebang and mode == b"100644":
            kind = "shebang_without_exec"
        elif not shebang and mode == b"100755":
            kind = "exec_without_shebang"
        if kind:
            records.append({"path": os.fsdecode(path), "mode": mode.decode(), "kind": kind})
    return records


def exemptions_from(path):
    exemptions = json.loads(path.read_text()) if path else {}
    if not isinstance(exemptions, dict):
        raise TypeError("Exemptions must map exact paths to reasons")
    for name, reason in exemptions.items():
        parts = PurePosixPath(name)
        if (not name or parts.is_absolute() or ".." in parts.parts
                or any(char in name for char in "*?[]\\")
                or not isinstance(reason, str) or not reason.strip()):
            raise ValueError("Each exemption needs an exact relative path and reason")
    return exemptions


def table_cell(value):
    return value.replace("\\", "\\\\").replace("|", "\\|").replace(
        "\n", "\\n"
    ).replace("\r", "\\r").replace("\t", "\\t")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--format", choices=("json", "table"), default="json")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--exemptions", type=Path)
    args = parser.parse_args()
    try:
        exemptions = exemptions_from(args.exemptions)
        records = audit(args.repo)
    except (TypeError, ValueError, OSError) as exc:
        print(f"Mode audit error: {exc}", file=sys.stderr)
        return 2
    for record in records:
        if record["kind"] == "shebang_without_exec" and record["path"] in exemptions:
            record["exemption"] = exemptions[record["path"]]
    if args.format == "json":
        print(json.dumps(records, indent=2, ensure_ascii=True))
    else:
        print("| Path | Index mode | Finding |\n| --- | --- | --- |")
        for record in records:
            print("| " + " | ".join(table_cell(record[key]) for key in (
                "path", "mode", "kind",
            )) + " |")
    return int(args.check and any(
        record["kind"] == "shebang_without_exec" and "exemption" not in record
        for record in records
    ))


if __name__ == "__main__":
    sys.exit(main())
