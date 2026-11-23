"""Explicit Windows operator restore after native evidence expires; never automatic.

The operator supplies reviewed capture/final journal digests and the current
canonical source digest. All bytes and parked links remain available for audit.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path

from claude_runtime_transaction import absent, ancestors, file_record, identity, link_record, require


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def link_identity(record):
    return {key: value for key, value in record.items() if key != "target"}


def read_pinned(path, expected):
    file_record(path)
    raw = path.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == expected, "reviewed journal digest changed")
    return json.loads(raw)


def recovery_reference(journal):
    """Bind the operator restore inputs to the successful pilot receipt."""
    journal = Path(journal)
    ancestors(journal)
    capture = journal / "0001-captured.json"
    events = sorted((p for p in journal.glob("*.json") if p.name.split("-", 1)[0].isdigit()),
                    key=lambda p: int(p.name.split("-", 1)[0]))
    require(bool(events), "recovery journal has no events")
    final = events[-1]
    file_record(capture)
    file_record(final)
    require(json.loads(capture.read_text())["event"] == "captured", "invalid capture event")
    require(json.loads(final.read_text())["phase"] == "FINALIZED", "journal not finalized")
    return {"journal": str(journal.resolve()),
            "capture": {"path": str(capture.resolve()), "sha256": sha(capture)},
            "final": {"path": str(final.resolve()), "sha256": sha(final)}}


class Restore:
    def __init__(self, home, source, capture, final, journal, source_sha, capture_sha, final_sha):
        self.home, self.source = Path(home).absolute(), Path(source).absolute()
        self.capture, self.final = Path(capture).absolute(), Path(final).absolute()
        self.journal = Path(journal).absolute()
        self.pins = source_sha, capture_sha, final_sha
        self.paths, self.records, self.parents = {}, {}, {}
        self.moves = []

    def prepare(self):
        require(os.name == "nt", "Operator restoration is Windows-only")
        absent(self.journal)
        require(self.capture.parent == self.final.parent, "journal roots differ")
        for directory in (self.journal.parent, self.capture.parent):
            for parent in (directory, *directory.parents):
                require(not os.path.lexists(parent / ".git"), "journal inside repository")
                require(parent.name not in {".claude", ".agents", "rules"}, "journal inside discovery")
        self.parents.update(ancestors(self.journal.parent))
        self.parents.update(ancestors(self.capture.parent))
        self.parents.update(ancestors(self.home / ".claude/rules"))
        self.parents.update(ancestors(self.source.parent))
        require(identity(self.journal.parent)["device"] == identity(self.home)["device"], "journal volume differs")
        self.source_record = file_record(self.source)
        require(self.source_record["sha256"] == self.pins[0], "current source digest differs")
        capture = read_pinned(self.capture, self.pins[1])
        final = read_pinned(self.final, self.pins[2])
        require(capture.get("event") == "captured" and final.get("phase") == "FINALIZED", "unsupported journal state")
        before = capture["detail"]
        require(Path(before["home"]) == self.home and Path(before["source"]) == self.source, "journal owner differs")
        self.legacy = self.home / ".claude/CLAUDE.md"
        absent(self.legacy)
        self.paths = {"legacy": self.capture.parent / "legacy.link",
                      "native": self.home / ".claude/rules/workspace-soul.md"}
        for key, expected in (("legacy", before["legacy"]), ("native", final["native_record"])):
            actual = link_record(self.paths[key])
            require(link_identity(actual) == link_identity(expected), "loader identity changed")
            require(Path(actual["resolved"]) == self.source, "loader source differs")
            self.records[key] = actual
        receipt = self.home / ".claude/workspace-soul-verification.json"
        if os.path.lexists(receipt):
            self.paths["receipt"], self.records["receipt"] = receipt, file_record(receipt)
        self.check()

    def check(self):
        for path, expected in self.parents.items():
            require(identity(Path(path)) == expected, "parent identity changed")
        require(file_record(self.source) == self.source_record, "source changed during restore")
        require(sha(self.capture) == self.pins[1] and sha(self.final) == self.pins[2], "journal changed")
        for key, path in self.paths.items():
            record = file_record(path) if key == "receipt" else link_record(path)
            require(record == self.records[key], "restore input drift: " + key)

    def event(self, name, data):
        path = self.journal / name
        with path.open("x", encoding="utf-8") as stream:
            json.dump(data, stream, indent=2)
            stream.flush()
            os.fsync(stream.fileno())

    def move(self, key, destination):
        self.check()
        absent(destination)
        previous = self.paths[key]
        os.rename(previous, destination)  # Windows refuses an occupied destination.
        self.paths[key] = destination
        self.moves.append((key, previous))
        self.check()

    def unwind(self):
        errors = []
        for key, previous in reversed(self.moves):
            try:
                self.check()
                absent(previous)
                os.rename(self.paths[key], previous)
                self.paths[key] = previous
                self.check()
            except BaseException as failure:
                errors.append(str(failure))
        return errors

    def run(self):
        self.prepare()
        self.journal.mkdir(mode=0o700)
        self.parents[str(self.journal)] = identity(self.journal)
        self.event("prestate.json", {"paths": {k: str(v) for k, v in self.paths.items()},
                                    "records": self.records, "source": self.source_record})
        try:
            # Restore a known loader before parking the native one.
            self.move("legacy", self.legacy)
            self.move("native", self.journal / "native.link")
            if "receipt" in self.paths:
                self.move("receipt", self.journal / "verification-receipt.json")
            self.check()
            result = {"state": "LEGACY_RESTORED", "journal": str(self.journal),
                      "source_sha256": self.pins[0], "next": "Review current baseline, then use a fresh pilot output/journal name"}
        except BaseException as failure:
            errors = self.unwind()
            result = {"state": "BLOCKED" if errors else "NATIVE_RESTORED",
                      "reason": str(failure), "recovery_errors": errors, "journal": str(self.journal)}
        self.event("result.json", result)
        return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("home", "source", "capture", "final", "journal"):
        parser.add_argument("--" + name, type=Path, required=True)
    for name in ("source-sha256", "capture-sha256", "final-sha256"):
        parser.add_argument("--" + name, required=True)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    require(args.execute, "Explicit operator execution required")
    result = Restore(args.home, args.source, args.capture, args.final, args.journal,
                     args.source_sha256, args.capture_sha256, args.final_sha256).run()
    print(json.dumps(result))
    return 0 if result["state"] == "LEGACY_RESTORED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
