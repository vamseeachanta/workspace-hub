#!/usr/bin/env python3
"""Validate artifact rebuild declarations; see BUILD_COMMANDS.md revision 1."""

from __future__ import annotations

import argparse
import json
import math
import ntpath
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath


class ValidationError(ValueError):
    """Invalid registry, configuration or repository boundary."""


@dataclass(frozen=True)
class Artifact:
    path: str
    kind: str
    cwd: str
    argv: tuple[str, ...]
    inputs: tuple[str, ...]
    budget_seconds: float | None = None


# Schema policy: BUILD_COMMANDS.md revision 1, Registry.
KINDS = {"report", "page", "figure", "data"}

# Maintainer defaults: BUILD_COMMANDS.md revision 1, Configuration and Exit codes.
DEFAULT_TIMEOUT_SECONDS = 120
DEFAULT_PATTERNS = (
    "docs/reports/**/*.html", "docs/reports/**/*.pdf",
    "**/figures/**/*.svg", "**/assets/**/*.svg",
)


@dataclass(frozen=True)
class Config:
    patterns: tuple[str, ...] = DEFAULT_PATTERNS
    default_timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS
    normalise: tuple[tuple[str, re.Pattern], ...] = ()


@dataclass(frozen=True, order=True)
class Finding:
    code: str
    path: str

    def __str__(self) -> str:
        return f"{self.code}: {json.dumps(self.path, ensure_ascii=True)}"


def relative_path(value: object, field: str, *, dot: bool = False) -> str:
    """Require canonical, portable, repository-relative POSIX spelling."""
    if (
        not isinstance(value, str)
        or not value
        or "\\" in value
        or "\x00" in value
        # RFC 20 (1969), section 2: columns 0/1 are controls; DEL is 7*16+15.
        or any(ord(char) < 32 or char == "\x7f" for char in value)
        or ntpath.splitdrive(value)[0]
        or value.startswith("/")
        or ".." in PurePosixPath(value).parts
        or str(PurePosixPath(value)) != value
        or (value == "." and not dot)
        or ".git" in PurePosixPath(value).parts
    ):
        raise ValidationError(f"{field}: expected a canonical repository-relative path")
    return value


def object_fields(value: object, required: set[str], optional: set[str], field: str) -> dict:
    if not isinstance(value, dict):
        raise ValidationError(f"{field}: expected an object")
    missing = required - value.keys()
    if missing:
        raise ValidationError(f"{field}: missing field {min(missing)}")
    if value.keys() - required - optional:
        raise ValidationError(f"{field}: unknown field")
    return value


def positive_seconds(value: object, field: str) -> float:
    try:
        valid = type(value) in (int, float) and math.isfinite(value) and value > 0
    except OverflowError:
        valid = False
    if not valid:
        raise ValidationError(f"{field}: expected finite positive seconds")
    return float(value)


def validate_registry(data: object) -> list[Artifact]:
    if not isinstance(data, list):
        raise ValidationError("registry: expected a list")
    artifacts = []
    seen = set()
    for index, raw in enumerate(data):
        field = f"registry entry {index}"
        item = object_fields(raw, {"path", "kind", "build", "inputs"}, {"budget_seconds"}, field)
        path = relative_path(item["path"], f"{field}.path")
        if path in seen:
            raise ValidationError(f"{field}.path: duplicate path")
        seen.add(path)
        if not isinstance(item["kind"], str) or item["kind"] not in KINDS:
            raise ValidationError(f"{field}.kind: unknown kind")
        if isinstance(item["build"], str):
            raise ValidationError(f"{field}.build: shell strings are not allowed")
        build = object_fields(item["build"], {"cwd", "argv"}, set(), f"{field}.build")
        cwd = relative_path(build["cwd"], f"{field}.build.cwd", dot=True)
        argv = build["argv"]
        if isinstance(argv, str):
            raise ValidationError(f"{field}.build.argv: shell strings are not allowed")
        if not isinstance(argv, list) or not argv or any(
            not isinstance(arg, str) or not arg or "\x00" in arg for arg in argv
        ):
            raise ValidationError(f"{field}.build.argv: expected nonempty strings in a list")
        inputs = item["inputs"]
        if not isinstance(inputs, list):
            raise ValidationError(f"{field}.inputs: expected a list")
        inputs = tuple(relative_path(value, f"{field}.inputs") for value in inputs)
        budget = None
        if "budget_seconds" in item:
            budget = positive_seconds(item["budget_seconds"], f"{field}.budget_seconds")
        artifacts.append(Artifact(path, item["kind"], cwd, tuple(argv), inputs, budget))
    return artifacts


def _unique_object(pairs: list[tuple]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValidationError("duplicate JSON key")
        result[key] = value
    return result


def read_json(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_unique_object)
    except (OSError, UnicodeError, ValueError) as error:
        if isinstance(error, ValidationError):
            raise
        raise ValidationError("cannot read valid UTF-8 JSON") from None


def load_registry(path: Path) -> list[Artifact]:
    return validate_registry(read_json(path))


def validate_config(data: object) -> Config:
    item = object_fields(data, set(), {"patterns", "default_timeout_seconds", "normalise"}, "config")
    patterns = item.get("patterns", list(DEFAULT_PATTERNS))
    if not isinstance(patterns, list):
        raise ValidationError("config.patterns: expected a list")
    patterns = tuple(relative_path(value, "config.patterns") for value in patterns)
    timeout = positive_seconds(
        item.get("default_timeout_seconds", DEFAULT_TIMEOUT_SECONDS), "config.default_timeout_seconds",
    )
    rules = item.get("normalise", [])
    if not isinstance(rules, list):
        raise ValidationError("config.normalise: expected a list")
    normalise = []
    for rule in rules:
        rule = object_fields(rule, {"pattern", "regex"}, set(), "config.normalise rule")
        pattern = relative_path(rule["pattern"], "config.normalise.pattern")
        regex = rule["regex"]
        if not isinstance(regex, str) or not regex.startswith("^") or not regex.endswith("$"):
            raise ValidationError("config.normalise.regex: expected a whole-line ^...$ expression")
        try:
            compiled = re.compile(regex)
        except re.error:
            raise ValidationError("config.normalise.regex: invalid expression") from None
        normalise.append((pattern, compiled))
    return Config(patterns, timeout, tuple(normalise))


def repo_path(repo: Path, relative: str) -> Path:
    """Reject symlinks at every level, including links remaining inside the tree."""
    relative_path(relative, "repository path", dot=True)
    target = repo
    for part in PurePosixPath(relative).parts:
        target = target / part
        if target.is_symlink():
            raise ValidationError("repository path: symlinks are not supported")
    return target


def command_file(repo: Path, artifact: Artifact) -> Path | None:
    """Repository commands resolve from build.cwd, exactly as at execution time."""
    command = artifact.argv[0]
    # './' is conventional for direct execution, unlike declaration paths.
    command = command.removeprefix("./")
    try:
        relative_path(command, "command")
        path = repo_path(repo, str(PurePosixPath(artifact.cwd) / command))
    except ValidationError:
        return None
    return path if path.is_file() else None


def command_exists(repo: Path, artifact: Artifact) -> bool:
    if not repo_path(repo, artifact.cwd).is_dir():
        return False
    command = artifact.argv[0]
    return (
        command_file(repo, artifact) is not None
        or command in {"python", "python3"}
        or ("/" not in command and "\\" not in command and shutil.which(command) is not None)
    )


def unregistered(repo: Path, artifacts: list[Artifact], config: Config) -> list[str]:
    declared = {artifact.path for artifact in artifacts}
    found = set()
    for pattern in config.patterns:
        try:
            matches = repo.glob(pattern)
            for path in matches:
                if ".git" in path.relative_to(repo).parts:
                    continue
                relative = path.relative_to(repo).as_posix()
                if (
                    glob_matches(relative, pattern)
                    and repo_path(repo, relative).is_file()
                    and relative not in declared
                ):
                    found.add(relative)
        except (ValueError, NotImplementedError):
            raise ValidationError("config.patterns: invalid glob") from None
    return sorted(found)


def check_static(repo: Path, artifacts: list[Artifact], config: Config) -> list[Finding]:
    findings = [Finding("UNREGISTERED", path) for path in unregistered(repo, artifacts, config)]
    for artifact in artifacts:
        if not repo_path(repo, artifact.path).is_file():
            findings.append(Finding("MISSING_OUTPUT", artifact.path))
        if not command_exists(repo, artifact):
            findings.append(Finding("MISSING_COMMAND", artifact.path))
        for path in artifact.inputs:
            if not repo_path(repo, path).exists():
                findings.append(Finding("MISSING_INPUT", path))
    return sorted(set(findings))


def git_environment() -> dict[str, str]:
    """Reuse generate-calc-report.py's binding isolation, including config bindings."""
    return {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}


def tracked_files(repo: Path) -> list[str]:
    """NUL-delimited index paths; no worktree registration or Git mutation."""
    try:
        root = subprocess.run(
            ["git", "-C", str(repo), "rev-parse", "--show-toplevel"],
            check=True, capture_output=True, env=git_environment(),
        )
        if Path(os.fsdecode(root.stdout).rstrip("\n")).resolve() != repo:
            raise ValidationError("--repo must identify the Git root")
        result = subprocess.run(
            ["git", "-C", str(repo), "ls-files", "--cached", "-z"],
            check=True, capture_output=True, env=git_environment(),
        )
    except (OSError, subprocess.CalledProcessError):
        raise ValidationError("cannot enumerate tracked files with git ls-files") from None
    paths = sorted({os.fsdecode(path) for path in result.stdout.split(b"\x00") if path})
    for path in paths:
        if not repo_path(repo, path).is_file():
            raise ValidationError("tracked export requires present regular files; no submodules")
    return paths


def _build_environment(work: Path) -> dict[str, str]:
    # Commands are trusted, not sandboxed. Keep conventional scratch/cache writes
    # inside the disposable directory; do not forward credentials or Git bindings.
    env = {key: os.environ[key] for key in ("PATH", "SYSTEMROOT", "WINDIR") if key in os.environ}
    for name, relative in (
        ("HOME", "user"), ("USERPROFILE", "user"), ("TMPDIR", "tmp"),
        ("TMP", "tmp"), ("TEMP", "tmp"), ("XDG_CACHE_HOME", "cache"),
        ("UV_CACHE_DIR", "cache/uv"), ("npm_config_cache", "cache/npm"),
    ):
        directory = work / relative
        directory.mkdir(parents=True, exist_ok=True)
        env[name] = str(directory)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["GIT_CEILING_DIRECTORIES"] = str(work)
    return env


def _run_command(argv: list[str], cwd: Path, env: dict[str, str], timeout: float) -> str | None:
    try:
        with subprocess.Popen(
            argv, cwd=cwd, env=env, stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            start_new_session=(os.name == "posix"),
        ) as process:
            try:
                return "BUILD_FAILED" if process.wait(timeout=timeout) else None
            except subprocess.TimeoutExpired:
                if os.name == "posix":
                    try:
                        os.killpg(process.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                else:
                    process.kill()
                process.wait()
                return "TIMEOUT"
    except OSError:
        return "BUILD_FAILED"


def normalised_bytes(data: bytes, path: str, config: Config) -> bytes:
    rules = [regex for pattern, regex in config.normalise if glob_matches(path, pattern)]
    if not rules:
        return data
    try:
        text = data.decode("utf-8")
    except UnicodeError:
        raise ValidationError("normalisation requires UTF-8 output") from None
    return "".join(
        line for line in text.splitlines(keepends=True)
        if not any(regex.fullmatch(line.rstrip("\r\n")) for regex in rules)
    ).encode("utf-8")


def glob_matches(path: str, pattern: str) -> bool:
    """Match whole relative paths with glob's zero-or-more-directory ** semantics."""
    import fnmatch

    parts = PurePosixPath(path).parts
    patterns = PurePosixPath(pattern).parts

    def match(names: tuple[str, ...], globs: tuple[str, ...]) -> bool:
        if not globs:
            return not names
        if globs[0] == "**":
            return match(names, globs[1:]) or bool(names and match(names[1:], globs))
        return bool(names and fnmatch.fnmatchcase(names[0], globs[0]) and match(names[1:], globs[1:]))

    return match(parts, patterns)


def check_dynamic(
    repo: Path, artifacts: list[Artifact], config: Config, *, normalise: bool = False,
) -> list[Finding]:
    # Reject configured roots before tempfile probes them for writability.
    for variable in ("TMPDIR", "TEMP", "TMP"):
        value = os.environ.get(variable)
        if value and Path(value).resolve().is_relative_to(repo):
            raise ValidationError("temporary directory must be outside the checked repository")
    temporary_root = Path(tempfile.gettempdir()).resolve()
    if temporary_root.is_relative_to(repo):
        raise ValidationError("temporary directory must be outside the checked repository")
    paths = tracked_files(repo)
    if any(artifact.path not in paths for artifact in artifacts):
        raise ValidationError("rebuild references must be tracked files")
    findings = []
    for artifact in artifacts:
        reference = repo_path(repo, artifact.path).read_bytes()
        with tempfile.TemporaryDirectory(prefix="artifact-rebuild-", dir=temporary_root) as temporary:
            work = Path(temporary)
            copy = work / "repository"
            copy.mkdir()
            for path in paths:
                target = copy / path
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(repo_path(repo, path), target)
            # A copied stale output is not evidence that a command regenerated it.
            output = copy / artifact.path
            output.unlink()
            command = command_file(copy, artifact)
            argv = list(artifact.argv)
            if command is not None:
                argv[0] = str(command)
            elif argv[0] in {"python", "python3"}:
                argv[0] = sys.executable
            budget = artifact.budget_seconds or config.default_timeout_seconds
            failure = _run_command(argv, copy / artifact.cwd, _build_environment(work), budget)
            if failure:
                findings.append(Finding(failure, artifact.path))
                continue
            # Build-created links must never redirect the comparison outside the copy.
            try:
                output = repo_path(copy, artifact.path)
                regenerated = output.read_bytes() if output.is_file() else None
            except (OSError, ValidationError):
                regenerated = None
            if regenerated is not None and normalise:
                regenerated = normalised_bytes(regenerated, artifact.path, config)
                reference = normalised_bytes(reference, artifact.path, config)
            if regenerated != reference:
                findings.append(Finding("NOT_REPRODUCED", artifact.path))
    return sorted(findings)


def suggest(repo: Path, paths: list[str]) -> list[dict]:
    """Basename references are hints, never proof of a working command."""
    candidates = []
    # Interpreter names are conventions, not installation guarantees; see
    # BUILD_COMMANDS.md revision 1, Suggestions.
    interpreters = {".py": "python3", ".sh": "sh", ".js": "node", ".rb": "ruby", ".pl": "perl"}
    for script in tracked_files(repo):
        source = repo_path(repo, script)
        interpreter = interpreters.get(source.suffix)
        try:
            text = source.read_text(encoding="utf-8")
        except UnicodeError:
            continue
        if "\x00" in text:
            continue
        if interpreter:
            argv = [interpreter, script]
        elif text.startswith("#!") and os.access(source, os.X_OK):
            argv = ["./" + script]
        else:
            continue
        for path in paths:
            if PurePosixPath(path).name in text:
                candidates.append({"path": path, "build": {"cwd": ".", "argv": argv}})
    return candidates


class SafeParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        # Do not repeat user arguments, which may contain credential material.
        self.exit(2, "CONFIG_ERROR: invalid command-line arguments\n")


def main(argv: list[str] | None = None) -> int:
    parser = SafeParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--repo", type=Path, default=Path("."))
    parser.add_argument("--patterns", type=Path, help="JSON configuration; replaces default patterns")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--run", action="store_true", help="run trusted commands in tracked-file copies")
    mode.add_argument("--suggest", action="store_true", help="report candidate scripts without writing")
    parser.add_argument("--normalise", action="store_true", help="enable configured whole-line rules")
    args = parser.parse_args(argv)
    try:
        if args.normalise and not args.run:
            raise ValidationError("--normalise requires --run")
        repo = args.repo.resolve()
        if not repo.is_dir():
            raise ValidationError("repository directory does not exist")
        registry = repo_path(repo, "artifacts.registry.json")
        artifacts = [] if args.suggest and not registry.exists() else load_registry(registry)
        config = validate_config(read_json(args.patterns)) if args.patterns else Config()
        findings = check_static(repo, artifacts, config)
        if args.run and not findings:
            findings.extend(check_dynamic(repo, artifacts, config, normalise=args.normalise))
        for finding in findings:
            print(finding)
        if args.suggest:
            for candidate in suggest(repo, [item.path for item in findings if item.code == "UNREGISTERED"]):
                print("CANDIDATE: " + json.dumps(candidate, ensure_ascii=True))
        if not findings:
            print("OK")
        return 1 if findings else 0
    except (ValidationError, OSError) as error:
        message = str(error) if isinstance(error, ValidationError) else "repository files unavailable"
        print(f"CONFIG_ERROR: {message}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
