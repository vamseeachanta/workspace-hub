"""Cooperatively serialized, evidence-preserving Claude user-link trial.

No automatic recovery across processes: an existing journal requires inspection.
Parent/link identity checks detect drift; they do not lock out arbitrary writers.
"""
import hashlib
import json
import os
import re
from pathlib import Path
import stat


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def identity(path):
    s = path.lstat()
    return {"device": s.st_dev, "inode": s.st_ino,
            "uid": s.st_uid, "gid": s.st_gid,
            "mode": s.st_mode, "attributes": getattr(s, "st_file_attributes", 0)}


def reparse(path):
    return bool(identity(path)["attributes"] & 1024) or path.is_symlink()


def file_record(path):
    require(not reparse(path) and path.is_file(), "source must be regular")
    before = identity(path)
    metadata = path.lstat()
    data = path.read_bytes()
    require(identity(path) == before, "source changed during read")
    after = path.lstat()
    require((metadata.st_size, metadata.st_mtime_ns, metadata.st_ctime_ns) ==
            (after.st_size, after.st_mtime_ns, after.st_ctime_ns),
            "source metadata changed during read")
    return {**before, "size": after.st_size, "mtime_ns": after.st_mtime_ns,
            "ctime_ns": after.st_ctime_ns,
            "sha256": hashlib.sha256(data).hexdigest()}


def link_record(path):
    require(path.is_symlink(), "expected managed symlink")
    target = path.resolve(strict=True)
    return {**identity(path), "raw_target": os.readlink(path),
            "resolved": str(target), "target": file_record(target)}


def absent(path):
    require(not os.path.lexists(path), "occupied path: " + str(path))


def ancestors(path):
    chain = list(reversed(path.parents)) + [path]
    result = {}
    for entry in chain:
        require(entry.is_dir() and not reparse(entry), "unsafe parent: " + str(entry))
        result[str(entry)] = identity(entry)
    return result


class Transaction:
    """Call capture once, then explicit trial transitions; retain all journals."""

    def __init__(self, home, source, journal_dir, expected_legacy_sha256=None):
        require(expected_legacy_sha256 is None or
                (isinstance(expected_legacy_sha256, str) and
                 re.fullmatch(r"[0-9a-f]{64}", expected_legacy_sha256) is not None),
                "expected legacy digest must be lowercase SHA-256")
        self.expected_legacy_sha256 = expected_legacy_sha256
        self.home = Path(os.path.abspath(home))
        self.source = Path(os.path.abspath(source))
        self.journal = Path(os.path.abspath(journal_dir))
        self.claude = self.home / ".claude"
        self.rules = self.claude / "rules"
        self.legacy = self.claude / "CLAUDE.md"
        self.native = self.rules / "workspace-soul.md"
        self.parents = {}
        self.sources = {}
        self.prestate = None
        self.native_record = None
        self.parked_record = None
        self.parked_phase = None
        self.legacy_parked = False
        self.created_rules = False
        self.phase = "NEW"
        self.sequence = 0

    def capture(self):
        require(self.phase == "NEW", "capture already performed")
        require(self.journal != self.home, "journal cannot be home")
        for parent in [self.journal.parent, *self.journal.parents]:
            require(not (parent / ".git").exists(), "journal inside repository")
            require(parent.name not in {".claude", ".agents", "rules"},
                    "journal inside discovery directory")
        absent(self.journal)
        self.parents.update(ancestors(self.claude))
        self.parents.update(ancestors(self.journal.parent))
        require(identity(self.journal.parent)["device"] ==
                identity(self.claude)["device"], "journal must be on legacy volume")
        self.parents.update(ancestors(self.source.parent))
        source = file_record(self.source)
        legacy = link_record(self.legacy)
        require(Path(legacy["raw_target"]).is_absolute(), "legacy target must be absolute before parking")
        self.parents.update(ancestors(Path(legacy["resolved"]).parent))
        expected = self.expected_legacy_sha256 or source["sha256"]
        require(expected == legacy["target"]["sha256"], "legacy digest mismatch")
        if os.path.lexists(self.rules):
            self.parents.update(ancestors(self.rules))
        absent(self.native)
        self.sources[str(self.source)] = source
        self.sources[legacy["resolved"]] = legacy["target"]
        self.prestate = {"home": str(self.home), "source": str(self.source),
                         "source_record": source, "expected_legacy_sha256": expected,
                         "legacy": legacy, "parents": dict(self.parents)}
        self.journal.mkdir(mode=0o700)
        self.parents[str(self.journal)] = identity(self.journal)
        self.phase = "CAPTURED"
        self._event("captured", self.prestate)
        return self.prestate

    def _event(self, event, detail=None):
        self.sequence += 1
        path = self.journal / ("%04d-%s.json" % (self.sequence, event))
        value = {"event": event, "phase": self.phase, "detail": detail,
                 "native_record": self.native_record,
                 "parked_phase": self.parked_phase,
                 "legacy_parked": self.legacy_parked}
        with path.open("x", encoding="utf-8") as handle:
            json.dump(value, handle, indent=2)
            handle.flush()
            os.fsync(handle.fileno())

    def _check(self):
        require(self.prestate is not None, "capture required")
        if str(self.rules) not in self.parents:
            absent(self.rules)
        for path, expected in self.parents.items():
            require(identity(Path(path)) == expected and not reparse(Path(path)),
                    "parent drift: " + path)
        for path, expected in self.sources.items():
            require(file_record(Path(path)) == expected, "source drift: " + path)
        if self.legacy_parked:
            absent(self.legacy)
            require(link_record(self.journal / "legacy.link") == self.prestate["legacy"],
                    "parked legacy drift")
        else:
            require(link_record(self.legacy) == self.prestate["legacy"], "legacy drift")
        if self.native_record is None:
            absent(self.native)
        else:
            require(link_record(self.native) == self.native_record, "native drift")
        if self.parked_record is not None:
            require(link_record(self.journal / "native.link") == self.parked_record,
                    "parked native drift")

    def _move(self, source, destination, expected):
        self._check()
        absent(destination)
        require(link_record(source) == expected, "move source drift")
        self._event("move-intent", {"from": str(source), "to": str(destination)})
        self._check()
        absent(destination)
        require(link_record(source) == expected, "move source drift")
        if os.name == "nt":
            os.rename(source, destination)  # Windows refuses an occupied destination.
        else:
            os.link(source, destination, follow_symlinks=False)
            require(link_record(source) == expected, "linked move source drift")
            source.unlink()  # Failure preserves both names for manual inspection.
        require(link_record(destination) == expected, "move result drift")

    def _make_native(self, target):
        self._check()
        self._event("native-create-intent", {"target": str(target)})
        self._check()
        os.symlink(target, self.native)
        self.native_record = link_record(self.native)
        self._event("native-created")

    def begin(self, trial_source):
        require(self.phase == "CAPTURED", "begin requires captured state")
        self._check()
        self.trial = Path(os.path.abspath(trial_source))
        self.parents.update(ancestors(self.trial.parent))
        self.sources[str(self.trial)] = file_record(self.trial)
        self._move(self.legacy, self.journal / "legacy.link", self.prestate["legacy"])
        self.legacy_parked = True
        self.phase = "LEGACY_PARKED"
        self._event("legacy-parked")
        if not os.path.lexists(self.rules):
            self._check()
            self._event("rules-create-intent")
            self._check()
            self.rules.mkdir(mode=0o700)
            self.created_rules = True
            self.parents[str(self.rules)] = identity(self.rules)
        self._make_native(self.trial)
        self.phase = "TRIAL"
        self._event("trial-ready")
        return self.readback()

    def park_native(self):
        require(self.phase in {"TRIAL", "FINALIZED"},
                "park requires trial or finalized state")
        return_phase = self.phase
        expected = self.native_record
        self._move(self.native, self.journal / "native.link", expected)
        self.parked_record = expected
        self.native_record = None
        self.parked_phase = return_phase
        self.phase = "NEGATIVE"
        self._event("native-parked", {"return_phase": return_phase})

    def restore_native(self):
        require(self.phase == "NEGATIVE", "restore requires negative state")
        require(self.parked_phase in {"TRIAL", "FINALIZED"},
                "parked return phase missing")
        return_phase = self.parked_phase
        self._move(self.journal / "native.link", self.native, self.parked_record)
        self.native_record = self.parked_record
        self.parked_record = None
        self.parked_phase = None
        self.phase = return_phase
        self._event("native-restored", {"restored_phase": return_phase})

    def finalize(self):
        require(self.phase == "TRIAL", "finalize requires trial state")
        self._move(self.native, self.journal / "trial-final.link", self.native_record)
        self.native_record = None
        self.phase = "FINALIZING"
        self._make_native(self.source)
        self.phase = "FINALIZED"
        self._event("finalized")
        return self.readback()

    def rollback(self):
        require(self.phase not in {"NEW", "ROLLED_BACK"}, "no active transaction")
        self._check()
        if self.native_record is not None:
            self._event("native-remove-intent")
            self._check()
            self.native.unlink()
            self.native_record = None
        if self.legacy_parked:
            self._move(self.journal / "legacy.link", self.legacy, self.prestate["legacy"])
            self.legacy_parked = False
        if self.created_rules:
            self._event("rules-remove-intent")
            self._check()
            require(not list(self.rules.iterdir()), "owned directory gained content")
            self.rules.rmdir()
            del self.parents[str(self.rules)]
            self.created_rules = False
        self.phase = "ROLLED_BACK"
        self._event("rolled-back")
        return self.readback()

    def readback(self):
        self._check()
        return {"phase": self.phase, "legacy_parked": self.legacy_parked,
                "native": self.native_record, "journal": str(self.journal)}
