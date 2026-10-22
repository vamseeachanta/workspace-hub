"""Byte-preserving archive evidence; protocol v1 in cleanup-safety.html.

GNU findutils -print0, GNU coreutils sort -z and GNU tar --null are required.
BSD tools are rejected rather than silently using incompatible options.
"""
import argparse
import base64
import json
import os
import subprocess
import tarfile
import tempfile
from pathlib import Path

from cleanup_evidence import digest_bytes, snapshot


def canonical(value):
    # RFC 8259 section 8.1: UTF-8 JSON; path bytes are base64, never decoded text.
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii") + b"\n"


def source_records(source):
    source = Path(source).resolve(strict=True)
    rows = snapshot(source.parent, [source.name])
    prefix = os.fsencode(source.name)
    for row in rows:
        path = base64.b64decode(row["path_b64"])
        relative = b"." if path == prefix else path[len(prefix) + 1:]
        row["path_b64"] = base64.b64encode(relative).decode("ascii")
    return sorted(rows, key=lambda row: base64.b64decode(row["path_b64"]))


def manifest_bytes(rows):
    return canonical({"schema": 1, "path_encoding": "base64"}) + b"".join(
        canonical(row) for row in rows)


def read_manifest(path):
    if Path(path).suffix != ".jsonl":
        raise ValueError("partial or unpublished manifest")
    data = Path(path).read_bytes()
    lines = data.splitlines()
    if not lines or json.loads(lines[0]) != {"schema": 1, "path_encoding": "base64"}:
        raise ValueError("unsupported manifest schema")
    rows = [json.loads(line) for line in lines[1:]]
    names = [base64.b64decode(row["path_b64"], validate=True) for row in rows]
    if not rows or names != sorted(set(names)) or manifest_bytes(rows) != data:
        raise ValueError("noncanonical or incomplete manifest")
    return rows


def atomic_write(path, data):
    """An interrupted write has a .partial suffix; only rename publishes it."""
    fd, temporary = tempfile.mkstemp(prefix="evidence-", suffix=".partial", dir=path.parent)
    with os.fdopen(fd, "wb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)
    directory = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)


def require_gnu():
    for tool in ("find", "sort", "tar"):
        version = subprocess.run([tool, "--version"], check=True, capture_output=True).stdout
        if b"GNU" not in version:
            raise ValueError("GNU find, sort and tar are required; archive NOT_EVALUATED")


def archive_payload(source, path):
    require_gnu()
    # Run each computation sequentially. Raw membership stays NUL-delimited.
    with tempfile.TemporaryFile(dir=path.parent) as discovered:
        subprocess.run(["find", ".", "-print0"], cwd=source, stdout=discovered, check=True)
        discovered.seek(0)
        with tempfile.TemporaryFile(dir=path.parent) as ordered:
            subprocess.run(["sort", "-z"], stdin=discovered, stdout=ordered,
                           env={**os.environ, "LC_ALL": "C"}, check=True)
            ordered.seek(0)
            subprocess.run(["tar", "--create", "--gzip", "--format=pax",
                            "--file", str(path), "--no-recursion", "--hard-dereference", "--null",
                            "--verbatim-files-from", "--files-from=-"], cwd=source,
                           stdin=ordered, check=True)


def archive_records(path):
    records = {}
    with tarfile.open(path, "r:gz", encoding="utf-8", errors="surrogateescape") as archive:
        for member in archive:
            name = os.fsencode(member.name)
            if name.startswith(b"./"):
                name = name[2:]
            name = name.rstrip(b"/") or b"."
            if name in records:
                raise ValueError("duplicate archive member")
            row = {"mode": member.mode}
            if member.isfile():
                stream = archive.extractfile(member)
                # Streaming avoids loading an archive member into memory.
                import hashlib
                digest = hashlib.sha256()
                for chunk in iter(lambda stream=stream: stream.read(65536), b""):
                    digest.update(chunk)
                row.update(kind="file", size=member.size, sha256=digest.hexdigest())
            elif member.isdir():
                row["kind"] = "directory"
            elif member.issym():
                row.update(kind="symlink", link_b64=base64.b64encode(
                    os.fsencode(member.linkname)).decode("ascii"))
            else:
                raise ValueError("unsupported archive member")
            records[name] = row
    return records


def check_members(archive, rows):
    expected = {}
    for row in rows:
        expected[base64.b64decode(row["path_b64"])] = {
            key: row[key] for key in ("mode", "kind", "size", "sha256", "link_b64")
            if key in row and (key != "size" or row["kind"] == "file")}
    if archive_records(archive) != expected:
        raise ValueError("archive and source membership, content or metadata differ")


def payload_hash(path):
    import hashlib
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def create(source, output):
    source, output = Path(source).resolve(strict=True), Path(output).resolve()
    if output.is_relative_to(source):
        raise ValueError("archive output must be outside source")
    output.mkdir(parents=True, exist_ok=True)
    rows = source_records(source)
    data = manifest_bytes(rows)
    digest = digest_bytes(data)
    manifest = output / (digest + ".jsonl")
    archive = output / (digest + ".tar.gz")
    sidecar = output / (digest + ".sha256")
    if manifest.exists() and archive.exists() and sidecar.exists():
        verify(source, archive, manifest, sidecar)
        return {"manifest": manifest, "manifest_sha256": digest,
                "archive": archive, "sidecar": sidecar}
    atomic_write(manifest, data)
    fd, temporary = tempfile.mkstemp(prefix="payload-", suffix=".partial", dir=output)
    os.close(fd)
    partial = Path(temporary)
    archive_payload(source, partial)
    if source_records(source) != rows:
        raise ValueError("source changed during archive creation")
    check_members(partial, rows)
    with partial.open("rb") as stream:
        os.fsync(stream.fileno())
    os.replace(partial, archive)
    atomic_write(sidecar, canonical({"schema": 1, "manifest_sha256": digest,
                                   "archive_sha256": payload_hash(archive)}))
    verify(source, archive, manifest, sidecar)
    return {"manifest": manifest, "manifest_sha256": digest,
            "archive": archive, "sidecar": sidecar}


def verify(source, archive, manifest, sidecar):
    rows = read_manifest(manifest)
    checksums = json.loads(Path(sidecar).read_bytes())
    digest = digest_bytes(Path(manifest).read_bytes())
    if (checksums != {"schema": 1, "manifest_sha256": digest,
                      "archive_sha256": payload_hash(archive)}
            or Path(sidecar).name != digest + ".sha256"):
        raise ValueError("checksum evidence mismatch")
    if source_records(source) != rows:
        raise ValueError("source differs from recorded manifest")
    check_members(archive, rows)
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    print(json.dumps(create(args.source, args.output), default=str))
