"""Strict Foundation-only mapping; historical fixture layouts remain untouched."""
import os
from pathlib import Path
import re
import subprocess

import yaml

from materialize_profile_fs import checked, digest, within, walk_no_links

PAYLOADS = (
    "data/ecosystem-data-sources/SKILL.md", "data/drive-file-search/SKILL.md",
    "research/wiki-context/SKILL.md", "coordination/pre-completion-cleanup-audit/SKILL.md",
    "data/drive-file-search/references/context-extraction.md",
    "coordination/pre-completion-cleanup-audit/references/user-facing-scratch-artifacts.md",
)
ROOTS = {"claude": ".claude/skills", "codex": ".agents/skills"}


def git_environment():
    """Discard inherited Git routing/config; preserve ordinary process settings.

    Local repository config remains visible; top-level verification rejects its
    core.worktree redirection. System/global config cannot rebind read-only calls.
    """
    result = {k: v for k, v in os.environ.items() if not k.upper().startswith("GIT_")}
    result.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull)
    return result


def git_read(root, *arguments):
    return subprocess.run(["git", "-C", str(root), *arguments],
                          env=git_environment(), capture_output=True)


def repository_top(root, required=True):
    result = git_read(root, "rev-parse", "--show-toplevel")
    if result.returncode:
        if not required and not (root / ".git").exists():
            return False
        raise ValueError("repository top-level could not be verified")
    if checked(Path(os.fsdecode(result.stdout).strip())) != root:
        raise ValueError("explicit root must equal physical repository top-level")
    return True


class StrictLoader(yaml.SafeLoader):
    """Reject duplicate mapping keys, including merged keys."""


def strict_mapping(loader, node):
    loader.flatten_mapping(node)
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node)
        if key in result:
            raise ValueError("duplicate YAML key")
        result[key] = loader.construct_object(value_node, deep=True)
    return result


StrictLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, strict_mapping)


def load_yaml(raw):
    try:
        return yaml.load(raw, Loader=StrictLoader)
    except yaml.YAMLError as error:
        raise ValueError("malformed YAML") from error


def frontmatter(raw):
    text = raw.decode("utf-8-sig").replace("\r\n", "\n")
    match = re.match(r"\A---\n(.*?)\n---(?:\n|$)", text, re.S)
    if not match:
        raise ValueError("missing skill frontmatter")
    value = load_yaml(match[1])
    if not isinstance(value, dict) or not isinstance(value.get("name"), str) or not value["name"]:
        raise ValueError("invalid skill name")
    return value["name"]


def profile_entries(source, profile, provider):
    raw = checked(profile).read_bytes()
    data = load_yaml(raw)
    if not isinstance(data, dict) or type(data.get("schema_version")) is not int or data["schema_version"] != 1:
        raise ValueError("unsupported profile schema")
    if data.get("name") != "foundation" or data.get("canonical_source") != ".claude/skills":
        raise ValueError("only canonical Foundation profile is supported")
    adapters = data.get("adapters")
    if not isinstance(adapters, dict):
        raise ValueError("adapters must be a mapping")
    mode = adapters.get("repository_installation")
    if not isinstance(mode, dict):
        raise ValueError("installation mapping must be an object")
    if mode.get("mode") != "family-preserving-project" or mode.get("provider_roots") != ROOTS:
        raise ValueError("explicit repository installation mapping required")
    if provider not in ROOTS:
        raise ValueError("unsupported provider")
    entries = activation_entries(data)
    relative = [entry.get("path", "").removeprefix(".claude/skills/") for entry in entries]
    if sorted(relative) != sorted(PAYLOADS):
        raise ValueError("activation set differs from Foundation boundary")
    result = [check_entry(source, entry, provider) for entry in entries]
    check_references(source, result)
    return digest(raw), result, data.get("historical_profile_sha256")


def activation_entries(data):
    activation = data.get("activation")
    if not isinstance(activation, dict):
        raise ValueError("activation must be an object")
    skills, refs = activation.get("skills"), activation.get("references")
    if not isinstance(skills, list) or not isinstance(refs, list) or len(skills) != 4 or len(refs) != 2:
        raise ValueError("exactly four skills and two references required")
    for group, expected in ((skills, PAYLOADS[:4]), (refs, PAYLOADS[4:])):
        if any(not isinstance(e, dict) or not isinstance(e.get("path"), str) for e in group):
            raise ValueError("invalid activation entry")
        if {e["path"] for e in group} != {".claude/skills/" + p for p in expected}:
            raise ValueError("skill/reference classification mismatch")
    return skills + refs


def check_entry(source, entry, provider):
    path = entry.get("path", "")
    if not path.startswith(".claude/skills/"):
        raise ValueError("canonical source prefix required")
    relative = path[len(".claude/skills/"):]
    payload = within(source, path).read_bytes()
    normalization = entry.get("sha256_normalization")
    if normalization not in (None, "crlf-to-lf"):
        raise ValueError("unknown digest normalization")
    comparable = payload.replace(b"\r\n", b"\n") if normalization else payload
    if digest(comparable) != entry.get("sha256"):
        raise ValueError("source digest differs from profile pin")
    name = frontmatter(payload) if relative.endswith("/SKILL.md") else None
    if name and name != relative.split("/")[1]:
        raise ValueError("selected name differs from Foundation identity")
    return {"source": path, "target": ROOTS[provider] + "/" + relative,
            "sha256": digest(payload), "profile_sha256": entry["sha256"], "name": name}


def check_references(source, entries):
    allowed = {entry["source"] for entry in entries if not entry["name"]}
    for entry in entries:
        if not entry["name"]:
            continue
        text = within(source, entry["source"]).read_bytes().decode("utf-8-sig")
        refs = re.findall(r"references/[A-Za-z0-9_.\-/]+", text)
        parent = entry["source"].rsplit("/", 1)[0]
        for ref in refs:
            if parent + "/" + ref not in allowed:
                raise ValueError("required reference outside declared closure")


def collisions(target, provider, entries):
    root = within(target, ROOTS[provider])
    intended = {entry["name"]: within(target, entry["target"]) for entry in entries if entry["name"]}
    directories = []
    for path in walk_no_links(root, directories):
        try:
            name = frontmatter(path.read_bytes())
        except ValueError:
            if path.parent.name in intended:
                raise ValueError("malformed selected skill basename collision")
            continue
        if name in intended and path != intended[name]:
            raise ValueError("duplicate selected native skill name")
    for directory in directories:
        if directory.name in intended and not (directory / "SKILL.md").is_file():
            raise ValueError("selected skill directory lacks frontmatter file")
    if not repository_top(target, required=False):
        return
    indexed = git_read(target, "ls-files", "-s", "-z", "--", ROOTS[provider])
    if indexed.returncode:
        raise ValueError("destination index could not be verified")
    if indexed.returncode == 0 and any(x.startswith(b"120000 ") for x in indexed.stdout.split(b"\0")):
        raise ValueError("indexed symlink inside destination skills")
