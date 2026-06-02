"""Pure command-enforcement logic for Deckhand shell hooks."""

from __future__ import annotations

import ast
import os
import re
import shlex
from dataclasses import asdict, dataclass
from typing import Any, Iterable

from . import engine


READ_ACTIONS = {
    "status",
    "log",
    "diff",
    "show",
    "fetch",
    "clone",
    "ls-remote",
    "branch",
}
GH_READ_ACTIONS = {
    ("pr", "view"),
    ("pr", "list"),
    ("issue", "view"),
    ("issue", "list"),
    ("repo", "view"),
    ("release", "view"),
    ("release", "list"),
}
SUSPICIOUS_ACTION = "unparseable_suspicious"
GENERIC_DESTRUCTIVE_ACTION = "destructive"
_GITISH_RE = re.compile(r"(^|[/\\\s'\"=(])(?:git|gh|hub)(?:$|[\s'\";|&)/\\])")
_TRUSTED_TOOLS = {"git", "gh", "hub"}
_HERMES_TOOL_MODULE = "hermes_tools"
_HERMES_REENTRY_CALLS = {"terminal", "execute_code", "run_agent", "tool"}
_HERMES_BOUND_REENTRY_CALLS = _HERMES_REENTRY_CALLS | {"execute"}
_SHELL_UNSAFE_CHARS = {"$", "`", "\n", "(", ")", "{", "}", "<", ">"}
_DESTRUCTIVE_HINT_RE = re.compile(
    r"\b(?:push|delete|remove|rm|close|disable|archive|rename|transfer|reset|clean|rebase|"
    r"checkout|restore|switch|deinit|prune|expire|filter-branch|update-ref|stash|reflog|"
    r"secret|ssh-key|deploy-key|ruleset|workflow|variable|label|auth|api)\b|--force|-f\b|-X\b|--method\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class GitAction:
    """One detected git/gh command action."""

    tool: str
    action_class: str
    argv: tuple[str, ...]
    reason: str | None = None


def classify_command(command: str) -> list[GitAction]:
    """Classify git/gh invocations in a shell command string.

    The parser is intentionally conservative. It parses ordinary shell words and
    simple command separators, but returns a sentinel action when shell features
    make git/gh intent ambiguous.
    """
    if not isinstance(command, str) or not command.strip():
        return []

    suspicious_reason = _safe_grammar_violation(command)
    if suspicious_reason:
        return [_suspicious(suspicious_reason)]

    try:
        tokens = _shell_tokens(command)
    except ValueError:
        return [_suspicious("unparseable shell command")] if _looks_gitish_or_destructive(command) else []

    if _contains_pipe(tokens) and _looks_gitish(command):
        return [_suspicious("pipe involving git/gh is not allowed")]

    actions: list[GitAction] = []
    for segment in _split_segments(tokens):
        if not segment:
            continue
        segment_actions = _classify_segment(segment)
        if not segment_actions:
            continue
        actions.extend(segment_actions)
        if any(action.action_class == SUSPICIOUS_ACTION for action in segment_actions):
            return actions
    return actions


def inspect(command: str, *, cwd: str, request_context: dict[str, Any], config: Any) -> dict[str, Any]:
    """Authorize git/gh actions, denying suspicious or generic destructive forms before engine policy."""
    del cwd
    actions = classify_command(command)
    action_dicts = [_action_dict(action) for action in actions]
    if any(action.action_class == SUSPICIOUS_ACTION for action in actions):
        return {
            "allow": False,
            "reason": "fail-closed: suspicious git/gh command could not be confidently parsed",
            "actions": action_dicts,
            "decisions": [],
        }
    if any(action.action_class == GENERIC_DESTRUCTIVE_ACTION for action in actions):
        return {
            "allow": False,
            "reason": "fail-closed: destructive git/gh action denied",
            "actions": action_dicts,
            "decisions": [],
        }
    if not actions:
        return {"allow": True, "reason": "no git/gh action detected", "actions": [], "decisions": []}

    decisions = []
    for action in actions:
        decision = engine.decide(_engine_request(action, request_context, config), config=config)
        decisions.append(decision)

    denied = next((decision for decision in decisions if not decision.get("allow")), None)
    return {
        "allow": denied is None,
        "reason": denied["reason"] if denied else "allowed",
        "actions": action_dicts,
        "decisions": decisions,
    }


def scan_python_source(src: str) -> bool:
    """Return True when Python source should go through the command gate."""
    if not isinstance(src, str):
        return False
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return True
    return _PythonCommandGateVisitor().scan(tree)


def _shell_tokens(command: str) -> list[str]:
    lexer = shlex.shlex(command, posix=True, punctuation_chars=";&|")
    lexer.whitespace_split = True
    lexer.commenters = ""
    return list(lexer)


def _split_segments(tokens: Iterable[str]) -> list[list[str]]:
    segments: list[list[str]] = [[]]
    for token in tokens:
        if token in {";", "&&", "||"}:
            segments.append([])
            continue
        segments[-1].append(token)
    return segments


def _classify_segment(segment: list[str]) -> list[GitAction]:
    argv = _strip_prefixes(segment)
    if not argv:
        return []

    command = argv[0]
    tool = os.path.basename(command)
    if _is_suspicious_tool_token(command):
        return [_suspicious("git/gh command position is not a trusted bare executable")]
    if tool == "git":
        if _has_git_alias_config(argv[1:]):
            return [_suspicious("git alias configuration can hide destructive actions")]
        return [
            GitAction(tool=tool, action_class=action_class, argv=tuple(argv))
            for action_class in _classify_git(argv[1:])
        ]
    if tool in {"gh", "hub"}:
        return [
            GitAction(tool=tool, action_class=action_class, argv=tuple(argv))
            for action_class in _classify_gh(tool, argv[1:])
        ]
    if _segment_mentions_gitish(segment):
        return [_suspicious("git/gh appears outside command position")]
    if _DESTRUCTIVE_HINT_RE.search(" ".join(segment)):
        return [_suspicious("destructive-looking command may rely on alias or wrapper indirection")]
    return []


def _strip_prefixes(segment: list[str]) -> list[str]:
    argv = list(segment)
    while argv and _is_assignment(argv[0]):
        argv.pop(0)

    while argv:
        command = os.path.basename(argv[0])
        if command == "sudo":
            argv.pop(0)
            while argv and argv[0].startswith("-"):
                option = argv.pop(0)
                if option in {"-u", "-g", "-h", "-p"} and argv:
                    argv.pop(0)
            while argv and _is_assignment(argv[0]):
                argv.pop(0)
            continue
        if command == "env":
            argv.pop(0)
            while argv:
                if _is_assignment(argv[0]):
                    argv.pop(0)
                    continue
                if argv[0] in {"-i", "--ignore-environment", "-0", "--null"}:
                    argv.pop(0)
                    continue
                if argv[0].startswith("-"):
                    argv.pop(0)
                    continue
                break
            continue
        break
    return argv


def _classify_git(args: list[str]) -> list[str]:
    filtered = _strip_global_options(args)
    if not filtered:
        return ["read"]
    subcommand = filtered[0]
    rest = filtered[1:]

    if subcommand == "push":
        classes: list[str] = []
        if _has_any(rest, {"--force", "--force-with-lease", "-f"}) or any(
            arg.startswith("--force-with-lease=") for arg in rest
        ):
            classes.append("force_push")
        if _has_any(rest, {"--delete", "-d"}):
            classes.append("tag_delete" if _push_delete_looks_like_tag(rest) else "branch_delete")
        if _has_any(rest, {"--mirror", "--prune"}):
            classes.append(GENERIC_DESTRUCTIVE_ACTION)
        for refspec in _push_refspecs(rest):
            if refspec.startswith("+"):
                classes.append("force_push")
            if _is_empty_source_refspec(refspec):
                classes.append("tag_delete" if _looks_like_tag_ref(refspec.lstrip(":")) else "branch_delete")
        return _unique_classes(classes) or ["write"]
    if subcommand == "update-ref" and _has_any(rest, {"-d", "--delete"}):
        return [GENERIC_DESTRUCTIVE_ACTION]
    if subcommand == "branch":
        if _has_any(rest, {"-D", "-d", "--delete"}):
            return ["branch_delete"]
        if _has_any(rest, {"-m", "-M", "--move", "-c", "-C", "--copy"}):
            return [GENERIC_DESTRUCTIVE_ACTION]
        return ["read"] if _branch_looks_like_list(rest) else ["write"]
    if subcommand == "tag":
        if _has_any(rest, {"-d", "--delete"}):
            return ["tag_delete"]
        return ["write"]
    if subcommand == "reset" and _has_any(rest, {"--hard"}):
        return ["reset_hard"]
    if subcommand == "clean":
        return ["git_clean"]
    if subcommand == "stash" and (not rest or rest[0] in {"clear", "drop"}):
        return [GENERIC_DESTRUCTIVE_ACTION]
    if subcommand == "reflog" and rest and rest[0] in {"delete", "expire"}:
        return [GENERIC_DESTRUCTIVE_ACTION]
    if subcommand in {"filter-branch", "rebase"}:
        return [GENERIC_DESTRUCTIVE_ACTION]
    if subcommand == "gc" and any(arg == "--prune" or arg.startswith("--prune=") for arg in rest):
        return [GENERIC_DESTRUCTIVE_ACTION]
    if subcommand == "maintenance" and _maintenance_can_prune(rest):
        return [GENERIC_DESTRUCTIVE_ACTION]
    if subcommand == "worktree" and rest and rest[0] in {"remove", "prune"}:
        return [GENERIC_DESTRUCTIVE_ACTION]
    if subcommand == "remote" and rest and rest[0] in {"remove", "rm"}:
        return [GENERIC_DESTRUCTIVE_ACTION]
    if subcommand == "submodule" and rest and rest[0] == "deinit":
        return [GENERIC_DESTRUCTIVE_ACTION]
    if subcommand == "checkout" and "--" in rest:
        return [GENERIC_DESTRUCTIVE_ACTION]
    if subcommand in {"restore", "switch", "rm", "mv"}:
        return [GENERIC_DESTRUCTIVE_ACTION]
    if subcommand == "notes" and rest and rest[0] in {"remove", "prune"}:
        return [GENERIC_DESTRUCTIVE_ACTION]
    if subcommand == "replace" and _has_any(rest, {"-d", "--delete"}):
        return [GENERIC_DESTRUCTIVE_ACTION]
    if subcommand == "merge" and "--abort" in rest:
        return [GENERIC_DESTRUCTIVE_ACTION]
    if subcommand in READ_ACTIONS:
        return ["read"]
    return ["write"]


def _classify_gh(tool: str, args: list[str]) -> list[str]:
    filtered = _strip_global_options(args)
    if not filtered:
        return ["write"]
    if tool == "hub" and filtered[0] == "delete":
        return ["repo_delete"]
    if filtered[0] == "api":
        return [GENERIC_DESTRUCTIVE_ACTION] if _gh_api_can_mutate(filtered[1:]) else ["read"]
    if filtered[0] in {"alias", "auth", "secret", "ssh-key", "variable", "ruleset"}:
        return [GENERIC_DESTRUCTIVE_ACTION]
    if len(filtered) >= 2 and filtered[0] == "repo" and filtered[1] == "delete":
        return ["repo_delete"]
    if len(filtered) >= 2 and filtered[0] == "repo" and filtered[1] in {"archive", "edit", "rename", "transfer"}:
        return ["repo_delete"]
    if len(filtered) >= 3 and filtered[0] == "repo" and filtered[1] == "deploy-key" and filtered[2] == "delete":
        return [GENERIC_DESTRUCTIVE_ACTION]
    if len(filtered) >= 2 and filtered[0] == "release" and filtered[1] == "delete":
        return ["release_delete"]
    if len(filtered) >= 2 and filtered[0] == "release" and filtered[1] == "delete-asset":
        return ["release_delete"]
    if len(filtered) >= 2 and (
        (filtered[0], filtered[1])
        in {
            ("run", "delete"),
            ("cache", "delete"),
            ("label", "delete"),
            ("workflow", "disable"),
            ("pr", "close"),
            ("issue", "close"),
        }
    ):
        return [GENERIC_DESTRUCTIVE_ACTION]
    if len(filtered) >= 2 and (filtered[0], filtered[1]) in GH_READ_ACTIONS:
        return ["read"]
    return ["write"]


def _strip_global_options(args: list[str]) -> list[str]:
    filtered = list(args)
    while filtered:
        token = filtered[0]
        if token == "-C" and len(filtered) >= 2:
            del filtered[:2]
            continue
        if token in {"-c", "--config-env"} and len(filtered) >= 2:
            del filtered[:2]
            continue
        if token == "--":
            filtered.pop(0)
            continue
        if token.startswith("-"):
            filtered.pop(0)
            continue
        break
    return filtered


def _engine_request(action: GitAction, request_context: dict[str, Any], config: Any) -> dict[str, Any]:
    repo = request_context.get("repo") or request_context.get("target_repo")
    if repo is None:
        resolver = config.get("repo_resolver") if isinstance(config, dict) else None
        if callable(resolver):
            repo = resolver(request_context)
    target_repos = request_context.get("target_repos") or ([repo] if repo else [])
    return {
        "operator_id": request_context.get("operator_id"),
        "platform": request_context.get("platform"),
        "scope_name": request_context.get("scope_name"),
        "origin": request_context.get("origin") or {},
        "target_repos": target_repos,
        "action_class": action.action_class,
        "change": request_context.get("change") or {"files_deleted": 0, "touches_protected": False},
        "elevation_token": request_context.get("elevation_token"),
    }


def _action_dict(action: GitAction) -> dict[str, Any]:
    data = asdict(action)
    data["argv"] = list(action.argv)
    return data


def _suspicious(reason: str) -> GitAction:
    return GitAction(tool="unknown", action_class=SUSPICIOUS_ACTION, argv=(), reason=reason)


def _safe_grammar_violation(command: str) -> str | None:
    if not _looks_gitish_or_destructive(command):
        return None
    if "\\\n" in command:
        return "backslash line continuation may hide git/gh intent"
    if any(char in command for char in _SHELL_UNSAFE_CHARS):
        return "unsupported shell expansion or control syntax in git/gh command"
    if re.search(r"(?<![&])&(?![&])", command):
        return "background operator may hide git/gh sequencing"
    if re.search(r"(^|[;\s])alias\s+[A-Za-z_][A-Za-z0-9_]*=", command) or re.search(
        r"(^|[;\s])function\s+", command
    ):
        return "alias/function definition may hide git/gh intent"
    if re.search(r"\b(?:command|builtin)\s+(?:git|gh|hub)\b", command):
        return "command/builtin prefix may hide git/gh intent"
    if re.search(r"\b(?:git|gh|hub)\s+-c\s+alias\.", command):
        return "git alias configuration may hide destructive actions"
    return None


def _looks_gitish_or_destructive(command: str) -> bool:
    lowered = command.lower()
    return (
        _looks_gitish(command)
        or any(token in lowered for token in ("git", "gh", "hub", "$git", "${git}", "git-", "gh-", "hub-"))
        or bool(_DESTRUCTIVE_HINT_RE.search(command))
    )


def _contains_pipe(tokens: list[str]) -> bool:
    return any(token == "|" or (set(token) == {"|"} and token != "||") for token in tokens)


def _looks_gitish(command: str) -> bool:
    return bool(_GITISH_RE.search(command))


def _segment_mentions_gitish(segment: list[str]) -> bool:
    return _looks_gitish(" ".join(segment))


def _is_suspicious_tool_token(token: str) -> bool:
    basename = os.path.basename(token)
    lowered = basename.lower()
    if token in _TRUSTED_TOOLS:
        return False
    if basename in _TRUSTED_TOOLS:
        return True
    return (
        lowered in _TRUSTED_TOOLS
        or lowered in {"git.exe", "gh.exe", "hub.exe"}
        or lowered.startswith(("git-", "gh-", "hub-"))
        or token.startswith(("$", "${"))
    )


def _is_assignment(token: str) -> bool:
    name, separator, _value = token.partition("=")
    return bool(separator and name and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name))


def _has_git_alias_config(args: list[str]) -> bool:
    for index, arg in enumerate(args):
        if arg == "-c" and index + 1 < len(args) and args[index + 1].startswith("alias."):
            return True
        if arg.startswith("alias."):
            return True
    return False


def _has_any(args: list[str], needles: set[str]) -> bool:
    return any(arg in needles for arg in args)


def _unique_classes(classes: list[str]) -> list[str]:
    unique: list[str] = []
    for action_class in classes:
        if action_class not in unique:
            unique.append(action_class)
    return unique


def _push_refspecs(args: list[str]) -> list[str]:
    refspecs: list[str] = []
    skip_next = False
    for arg in args:
        if skip_next:
            skip_next = False
            continue
        if arg in {"--repo", "-R", "--receive-pack", "--exec", "--push-option", "-o"}:
            skip_next = True
            continue
        if arg == "--":
            continue
        if arg.startswith("-"):
            continue
        if ":" in arg or arg.startswith("+"):
            refspecs.append(arg)
    return refspecs


def _is_empty_source_refspec(refspec: str) -> bool:
    candidate = refspec[1:] if refspec.startswith("+") else refspec
    source, separator, dest = candidate.partition(":")
    return bool(separator and not source and dest)


def _looks_like_tag_ref(arg: str) -> bool:
    return arg.startswith("refs/tags/") or arg.startswith("tags/")


def _push_delete_looks_like_tag(args: list[str]) -> bool:
    for index, arg in enumerate(args):
        if _looks_like_tag_ref(arg):
            return True
        if arg == "--delete" and index + 1 < len(args) and _looks_like_version_tag(args[index + 1]):
            return True
    return False


def _looks_like_version_tag(arg: str) -> bool:
    return bool(re.fullmatch(r"v?\d+(?:\.\d+){1,3}(?:[-+][A-Za-z0-9._-]+)?", arg))


def _branch_looks_like_list(args: list[str]) -> bool:
    if not args:
        return True
    if any(arg in {"--list", "-l"} for arg in args):
        return True
    read_flags = {
        "-a",
        "-r",
        "--all",
        "--remotes",
        "--list",
        "-l",
        "-v",
        "-vv",
        "--verbose",
        "--contains",
        "--merged",
        "--no-merged",
        "--show-current",
    }
    return all(arg in read_flags or arg.startswith("--format=") or arg.startswith("--sort=") for arg in args)


def _maintenance_can_prune(args: list[str]) -> bool:
    return any(arg in {"gc", "prune"} or arg in {"--task=gc", "--task=prune"} for arg in args)


def _gh_api_can_mutate(args: list[str]) -> bool:
    method = "GET"
    index = 0
    while index < len(args):
        arg = args[index]
        if arg in {"-X", "--method"} and index + 1 < len(args):
            method = args[index + 1].upper()
            index += 2
            continue
        if arg.startswith("--method="):
            method = arg.partition("=")[2].upper()
        if arg in {"-f", "--field", "-F", "--raw-field"} or arg.startswith(("--field=", "--raw-field=")):
            return True
        index += 1
    return method != "GET"


class _PythonCommandGateVisitor(ast.NodeVisitor):
    # execute_code is gated when source touches process/tool re-entry:
    # subprocess/os.system/os.popen/os.exec*/shell=True, literal git/gh/hub argv,
    # hermes_tools imports/attributes/dynamic imports, direct Hermes helper names
    # (terminal/execute_code/run_agent/tool), and aliases/getattr dispatch of
    # Hermes helpers including execute. Syntax errors fail closed in caller.
    def __init__(self) -> None:
        self.module_aliases: dict[str, str] = {}
        self.callable_aliases: dict[str, tuple[str, str]] = {}
        self.constants: dict[str, str | tuple[str, ...]] = {}
        self.should_gate = False

    def scan(self, tree: ast.AST) -> bool:
        self.visit(tree)
        return self.should_gate

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            if alias.name in {"subprocess", "os"}:
                self.module_aliases[alias.asname or alias.name] = alias.name
                self.should_gate = True
            if self._is_hermes_module_name(alias.name):
                self.module_aliases[alias.asname or alias.name.split(".", 1)[0]] = _HERMES_TOOL_MODULE
                self.should_gate = True
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module in {"subprocess", "os"}:
            self.should_gate = True
            for alias in node.names:
                name = alias.asname or alias.name
                self.callable_aliases[name] = (node.module, alias.name)
        if node.module and self._is_hermes_module_name(node.module):
            self.should_gate = True
            for alias in node.names:
                name = alias.asname or alias.name
                self.callable_aliases[name] = (_HERMES_TOOL_MODULE, alias.name)
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        value = self._constant_value(node.value)
        for target in node.targets:
            if isinstance(target, ast.Name) and value is not None:
                self.constants[target.id] = value
            if isinstance(target, ast.Name) and self._is_subprocess_dynamic_import(node.value):
                self.callable_aliases[target.id] = ("subprocess", "*")
                self.should_gate = True
            if isinstance(target, ast.Name) and self._is_hermes_tool_reference(node.value):
                self.callable_aliases[target.id] = (_HERMES_TOOL_MODULE, "*")
                self.should_gate = True
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        if self._call_should_gate(node):
            self.should_gate = True
            return
        for arg in node.args:
            if self._argv_or_command_is_gitish(arg):
                self.should_gate = True
                return
        self.generic_visit(node)

    def _call_should_gate(self, node: ast.Call) -> bool:
        if any(keyword.arg == "shell" and self._truthy(keyword.value) for keyword in node.keywords):
            return True
        if self._is_dynamic_import_call(node):
            return True
        if self._is_hermes_getattr_call(node):
            return True
        func = node.func
        if isinstance(func, ast.Attribute):
            if self._is_subprocess_dynamic_import(func.value):
                return True
            if self._is_hermes_tool_reference(func.value):
                return True
            if isinstance(func.value, ast.Name):
                module = self.module_aliases.get(func.value.id)
                if module == "subprocess":
                    return True
                if module == "os" and (func.attr in {"system", "popen"} or func.attr.startswith("exec")):
                    return True
                if module == _HERMES_TOOL_MODULE:
                    return True
        if isinstance(func, ast.Name):
            module_func = self.callable_aliases.get(func.id)
            if module_func and (module_func[0] == "subprocess" or module_func in {("os", "system"), ("os", "popen")}):
                return True
            if module_func and module_func[0] == _HERMES_TOOL_MODULE:
                return True
            if func.id in _HERMES_REENTRY_CALLS:
                return True
        return False

    def _argv_or_command_is_gitish(self, node: ast.AST) -> bool:
        value = self._constant_value(node)
        if isinstance(value, str):
            return _literal_starts_gitish(value)
        if isinstance(value, tuple) and value:
            return _literal_starts_gitish(value[0])
        if isinstance(node, ast.Name):
            stored = self.constants.get(node.id)
            if isinstance(stored, str):
                return _literal_starts_gitish(stored)
            if isinstance(stored, tuple) and stored:
                return _literal_starts_gitish(stored[0])
        return False

    def _constant_value(self, node: ast.AST) -> str | tuple[str, ...] | None:
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return node.value
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
            left = self._constant_value(node.left)
            right = self._constant_value(node.right)
            if isinstance(left, str) and isinstance(right, str):
                return left + right
        if isinstance(node, (ast.List, ast.Tuple)):
            values: list[str] = []
            for element in node.elts:
                value = self._constant_value(element)
                if not isinstance(value, str):
                    return None
                values.append(value)
            return tuple(values)
        return None

    def _is_dynamic_import_call(self, node: ast.Call) -> bool:
        if isinstance(node.func, ast.Name) and node.func.id == "__import__" and node.args:
            value = self._constant_value(node.args[0])
            return value in {"subprocess", "os", _HERMES_TOOL_MODULE}
        return False

    def _is_subprocess_dynamic_import(self, node: ast.AST) -> bool:
        if isinstance(node, ast.Call):
            return self._is_dynamic_import_call(node)
        if isinstance(node, ast.Attribute):
            return self._is_subprocess_dynamic_import(node.value)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "getattr":
            return bool(node.args and self._is_subprocess_dynamic_import(node.args[0]))
        return False

    def _is_hermes_tool_reference(self, node: ast.AST) -> bool:
        if isinstance(node, ast.Name):
            return self.module_aliases.get(node.id) == _HERMES_TOOL_MODULE
        if isinstance(node, ast.Attribute):
            return self._is_hermes_tool_reference(node.value)
        if isinstance(node, ast.Call):
            return self._is_dynamic_import_call(node) or self._is_hermes_getattr_call(node)
        return False

    def _is_hermes_getattr_call(self, node: ast.Call) -> bool:
        if not (isinstance(node.func, ast.Name) and node.func.id == "getattr" and len(node.args) >= 2):
            return False
        attr = self._constant_value(node.args[1])
        return isinstance(attr, str) and attr in _HERMES_BOUND_REENTRY_CALLS and self._is_hermes_tool_reference(
            node.args[0]
        )

    @staticmethod
    def _is_hermes_module_name(name: str) -> bool:
        return name == _HERMES_TOOL_MODULE or name.startswith(f"{_HERMES_TOOL_MODULE}.")

    @staticmethod
    def _truthy(node: ast.AST) -> bool:
        return isinstance(node, ast.Constant) and bool(node.value)


def _literal_starts_gitish(value: str) -> bool:
    stripped = value.strip()
    return stripped == "git" or stripped == "gh" or stripped == "hub" or stripped.startswith(
        ("git ", "gh ", "hub ")
    )
