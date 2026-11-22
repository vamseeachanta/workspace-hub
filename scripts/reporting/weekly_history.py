"""Write history metadata for explicitly supplied, already validated reviews.

``write_history(directory, run_id=..., published_at=..., artifact=...)`` stores
an ascending JSON array in index.json and its last entry in latest.json. Entries
contain only those three fields; this is not the weekly review artifact schema.
The caller validates review content and authorizes publication before calling.

Identifiers are nonempty ASCII tokens starting with a letter or digit, followed
by letters, digits, dots, underscores or hyphens. Publication times are UTC ISO
calendar timestamps with seconds, optional microseconds, and Z or +00:00. They
are normalized to Z. Artifact locators are canonical relative POSIX paths with
ASCII letters, digits, dots, underscores and hyphens in each component. Empty,
dot and parent components, URL syntax and symlink escapes are rejected. Locators
are relative to directory; artifact existence and content are not inspected.

Order is by publication instant, then identifier (ascending ASCII order). Equal
identifiers with equal normalized metadata are no-ops; conflicts raise ValueError.
Malformed existing history also fails before writes. JSON uses sorted keys,
two-space indentation and a trailing newline as the local serialization contract.

Both files are staged before either is replaced; each os.replace is atomic on
the destination filesystem. index.json is authoritative and latest.json is
replaced last. This is not a multi-file transaction: interruption between the
replacements can leave a stale latest.json. Callers must serialize writers and
coordinate readers requiring a consistent pair. Crash recovery is out of scope.
"""

from __future__ import annotations

from datetime import datetime
import json
import os
from pathlib import Path
import re
import tempfile


_IDENTIFIER = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")
_COMPONENT = re.compile(r"[A-Za-z0-9._-]+")
# Calendar field widths follow datetime.isoformat's ISO calendar representation;
# fractional precision comes from datetime.resolution (one microsecond).
_TIMESTAMP = re.compile(
    r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}"
    r"(?:\.[0-9]{1,6})?(?:Z|\+00:00)"
)
_FIELDS = {"run_id", "published_at", "artifact"}


def _unique_fields(pairs: list[tuple]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON field")
        result[key] = value
    return result


def _summary(directory: Path, run_id: str, published_at: str, artifact: str) -> dict:
    if not isinstance(run_id, str) or not _IDENTIFIER.fullmatch(run_id):
        raise ValueError("run_id must be an ASCII identifier token")
    if not isinstance(published_at, str) or not _TIMESTAMP.fullmatch(published_at):
        raise ValueError("published_at must be a UTC timestamp with seconds")
    try:
        instant = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("published_at is not a valid calendar timestamp") from exc

    if not isinstance(artifact, str) or not artifact:
        raise ValueError("artifact must be a relative POSIX locator")
    components = artifact.split("/")
    if any(part in {"", ".", ".."} or not _COMPONENT.fullmatch(part)
           for part in components):
        raise ValueError("artifact must contain canonical relative path components")
    try:
        contained = (directory / artifact).resolve().is_relative_to(directory.resolve())
    except (OSError, RuntimeError) as exc:
        raise ValueError("artifact cannot be resolved safely") from exc
    if not contained:
        raise ValueError("artifact must stay inside the history directory")
    return {
        "run_id": run_id,
        "published_at": instant.isoformat().replace("+00:00", "Z"),
        "artifact": artifact,
    }


def _read_history(directory: Path) -> list[dict]:
    index = directory / "index.json"
    latest = directory / "latest.json"
    if index.is_symlink() or latest.is_symlink():
        raise ValueError("history output files must not be symlinks")
    if not index.exists():
        if latest.exists():
            raise ValueError("index.json is missing while latest.json exists")
        return []
    try:
        entries = json.loads(
            index.read_text(encoding="utf-8"), object_pairs_hook=_unique_fields
        )
    except (ValueError, UnicodeError) as exc:
        raise ValueError("index.json is not valid history JSON") from exc
    if not isinstance(entries, list):
        raise ValueError("index.json must contain an array")
    normalized = []
    identifiers = set()
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != _FIELDS:
            raise ValueError("index.json contains invalid summary fields")
        record = _summary(directory, **entry)
        if record["run_id"] in identifiers:
            raise ValueError("index.json contains duplicate identifiers")
        identifiers.add(record["run_id"])
        normalized.append(record)
    return normalized


def write_history(
    directory: Path, *, run_id: str, published_at: str, artifact: str
) -> bool:
    """Append validated review metadata; return False for an identical rerun.

    ValueError rejects invalid boundary fields, conflicting identifiers or invalid
    stored history before writes. Filesystem failures propagate as OSError.
    See the module contract for serialization and interruption limits.
    """
    directory = Path(directory)
    entry = _summary(directory, run_id, published_at, artifact)
    entries = _read_history(directory)
    for previous in entries:
        if previous["run_id"] == entry["run_id"]:
            if previous == entry:
                return False
            raise ValueError("conflicting metadata for existing run_id")
    entries.append(entry)
    entries.sort(key=lambda item: (
        datetime.fromisoformat(item["published_at"].replace("Z", "+00:00")),
        item["run_id"],
    ))

    directory.mkdir(parents=True, exist_ok=True)
    staged = []
    try:
        for filename, value in (("index.json", entries), ("latest.json", entries[-1])):
            with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", dir=directory,
                prefix=f".{filename}.", suffix=".tmp", delete=False,
            ) as stream:
                path = Path(stream.name)
                staged.append((path, directory / filename))
                # Two-space indentation is specified by the module contract.
                json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
                stream.write("\n")
                stream.flush()
                os.fsync(stream.fileno())
        for source, destination in staged:
            os.replace(source, destination)
    finally:
        for source, _ in staged:
            source.unlink(missing_ok=True)
    return True
