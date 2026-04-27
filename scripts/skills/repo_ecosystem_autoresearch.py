#!/usr/bin/env python3
"""Generic repo-ecosystem autoresearch runner.

This runner keeps the current skill-autoresearch safety model while making the
target type, evaluator, and result artifact explicit for non-skill repo assets.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Iterable

try:
    import yaml
except ImportError:  # pragma: no cover - pyproject includes pyyaml
    yaml = None


SUPPORTED_TARGET_TYPES = ("skill", "agent", "template", "workflow-config")
TEXT_TARGET_SUFFIXES = {".md", ".txt", ".yaml", ".yml", ".json"}
WORKFLOW_CONFIG_ALLOWLIST = (
    Path("config/scheduled-tasks/schedule-tasks.yaml"),
    Path(".planning/gsd-defaults.json"),
    Path(".planning/ROADMAP.md"),
    Path(".planning/milestones/v1.0-ROADMAP.md"),
)
DEFAULT_STATE_DIR = Path(".claude/state/skill-autoresearch")
DEFAULT_RESULTS_FILE = DEFAULT_STATE_DIR / "results.jsonl"
DEFAULT_LEGACY_SKILL_RESULTS_TSV = DEFAULT_STATE_DIR / "results.tsv"
DEFAULT_TIME_BUDGET_SECONDS = 180


class Evaluation:
    def __init__(self, warnings: int, criticals: int = 0, findings: Iterable[str] | None = None):
        self.warnings = int(warnings)
        self.criticals = int(criticals)
        self.findings = list(findings or [])

    @property
    def issue_count(self) -> int:
        return self.warnings + self.criticals


class Target:
    def __init__(self, target_type: str, path: Path, root: Path | None = None):
        if target_type not in SUPPORTED_TARGET_TYPES:
            raise ValueError(f"unsupported target type: {target_type}")
        self.target_type = target_type
        self.path = Path(path)
        self.root = Path(root) if root else None

    @property
    def relative_path(self) -> str:
        return target_path_for_results(self.path, self.root)


class AttemptOutcome:
    def __init__(
        self,
        target: Target,
        before: Evaluation,
        after: Evaluation,
        result: str,
        duration_s: int,
    ):
        self.target = target
        self.before = before
        self.after = after
        self.result = result
        self.duration_s = duration_s


class CandidateUnavailable(RuntimeError):
    pass


def git_root(start: Path) -> Path:
    result = subprocess.run(
        ["git", "-C", str(start), "rev-parse", "--show-toplevel"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    return Path(result.stdout.strip())


def target_path_for_results(path: Path, root: Path | None = None) -> str:
    path = Path(path)
    if root is not None:
        try:
            return path.resolve().relative_to(Path(root).resolve()).as_posix()
        except ValueError:
            pass

    parts = path.parts
    for anchor in (".claude", "config", ".planning", "docs", "scripts", "tests"):
        if anchor in parts:
            return Path(*parts[parts.index(anchor) :]).as_posix()
    return path.as_posix()


def discover_targets(root: Path, target_type: str) -> list[Target]:
    root = Path(root)
    if target_type == "skill":
        paths = sorted((root / ".claude" / "skills").glob("**/SKILL.md"))
    elif target_type == "agent":
        paths = sorted(
            p
            for p in (root / ".claude" / "agents").glob("**/*.md")
            if p.is_file() and p.name != "README.md"
        )
    elif target_type == "template":
        template_root = root / ".claude" / "get-shit-done" / "templates"
        paths = sorted(
            p
            for p in template_root.glob("**/*")
            if p.is_file() and p.suffix.lower() in TEXT_TARGET_SUFFIXES
        )
    elif target_type == "workflow-config":
        paths = [root / item for item in WORKFLOW_CONFIG_ALLOWLIST if (root / item).is_file()]
    else:
        raise ValueError(f"unsupported target type: {target_type}")
    return [Target(target_type, path, root) for path in paths]


def _text_findings(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    findings: list[str] = []
    if not text.strip():
        findings.append("empty file")
    if re.search(r"(?im)(^|\s|#|//|<!--|;)\s*\b(TODO|FIXME)\b\s*[:!]", text):
        findings.append("TODO/FIXME marker")
    if re.search(r"(?im)\bTBD\b", text):
        findings.append("TBD marker")
    if len(text.splitlines()) > 300:
        findings.append("file exceeds 300 lines")
    return findings


def evaluate_text_target(path: Path) -> Evaluation:
    findings = _text_findings(path)
    return Evaluation(warnings=len(findings), criticals=0, findings=findings)


def evaluate_agent_target(path: Path) -> Evaluation:
    text = path.read_text(encoding="utf-8")
    findings = _text_findings(path)
    if not text.lstrip().startswith("---"):
        findings.append("missing YAML frontmatter")
    if "name:" not in text[:500]:
        findings.append("missing agent name metadata")
    return Evaluation(warnings=len(findings), criticals=0, findings=findings)


def evaluate_template_target(path: Path) -> Evaluation:
    text = path.read_text(encoding="utf-8")
    findings = _text_findings(path)
    if path.suffix.lower() == ".md" and "{{" not in text and "{%" not in text:
        findings.append("template has no explicit placeholder markers")
    return Evaluation(warnings=len(findings), criticals=0, findings=findings)


def evaluate_workflow_config_target(path: Path) -> Evaluation:
    findings = _text_findings(path)
    criticals = 0
    if path.suffix.lower() in {".yaml", ".yml"} and yaml is not None:
        try:
            loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
            if loaded is None:
                findings.append("empty YAML document")
            elif path.name == "schedule-tasks.yaml" and "tasks" not in loaded:
                findings.append("scheduled task config missing tasks key")
        except yaml.YAMLError as exc:
            criticals += 1
            findings.append(f"invalid YAML: {exc.__class__.__name__}")
    elif path.suffix.lower() == ".json":
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            criticals += 1
            findings.append(f"invalid JSON: {exc.msg}")
    return Evaluation(warnings=len(findings) - criticals, criticals=criticals, findings=findings)


def skill_identifier(path: Path) -> str:
    text = path.read_text(encoding="utf-8", errors="replace")[:1000]
    match = re.search(r"(?m)^name:\s*['\"]?([^'\"\n]+?)['\"]?\s*$", text)
    if match:
        return match.group(1).strip()
    return path.parent.name


def _loads_json_payload(payload: str) -> object:
    try:
        return json.loads(payload)
    except json.JSONDecodeError:
        start = payload.find("{")
        end = payload.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise
        return json.loads(payload[start : end + 1])


def _parse_skill_eval_json(payload: str, skill_name: str) -> Evaluation:
    data = _loads_json_payload(payload)
    if not isinstance(data, dict):
        return Evaluation(warnings=0, criticals=1, findings=["skill-eval returned non-object JSON"])
    summary_issues = data.get("summary", {}).get("issues", {})
    if summary_issues:
        return Evaluation(
            warnings=summary_issues.get("warning", summary_issues.get("warnings", 0)),
            criticals=summary_issues.get("critical", summary_issues.get("criticals", 0)),
            findings=[],
        )

    skills = data.get("results", data.get("skill_details", data.get("skills", [])))
    findings: list[str] = []
    criticals = 0
    warnings = 0
    for skill in skills:
        if skill.get("name") != skill_name:
            continue
        for issue in skill.get("issues", []):
            severity = str(issue.get("severity", "")).lower()
            message = issue.get("message") or issue.get("check") or "skill-eval issue"
            findings.append(str(message))
            if severity == "critical":
                criticals += 1
            elif severity == "warning":
                warnings += 1
        break
    return Evaluation(warnings=warnings, criticals=criticals, findings=findings)


def _parse_all_skill_eval_json(payload: str) -> dict[str, Evaluation]:
    data = _loads_json_payload(payload)
    if not isinstance(data, dict):
        return {}
    skills = data.get("results", data.get("skill_details", data.get("skills", [])))
    parsed: dict[str, Evaluation] = {}
    for skill in skills:
        name = skill.get("name")
        if not name:
            continue
        findings: list[str] = []
        criticals = 0
        warnings = 0
        for issue in skill.get("issues", []):
            severity = str(issue.get("severity", "")).lower()
            message = issue.get("message") or issue.get("check") or "skill-eval issue"
            findings.append(str(message))
            if severity == "critical":
                criticals += 1
            elif severity == "warning":
                warnings += 1
        parsed[str(name)] = Evaluation(warnings=warnings, criticals=criticals, findings=findings)
    return parsed


def make_skill_evaluator(root: Path, skill_eval_script: Path | None = None) -> Callable[[Path], Evaluation]:
    script = skill_eval_script or root / ".claude/skills/development/skill-eval/scripts/eval-skills.py"
    cache: dict[tuple[str, int], Evaluation] = {}
    baseline_by_name: dict[str, Evaluation] = {}
    baseline_mtime_by_path: dict[str, int] = {}
    full_baseline_loaded = False

    def evaluator(path: Path) -> Evaluation:
        nonlocal baseline_by_name, baseline_mtime_by_path, full_baseline_loaded
        if not script.is_file():
            return evaluate_text_target(path)
        skill_name = skill_identifier(path)
        current_mtime = path.stat().st_mtime_ns
        path_key = str(path.resolve())
        cache_key = (skill_name, current_mtime)
        if cache_key in cache:
            return cache[cache_key]

        if not full_baseline_loaded:
            result = subprocess.run(
                ["uv", "run", "--no-project", "python", str(script), "--format", "json"],
                cwd=str(root),
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            full_baseline_loaded = True
            if result.stdout.strip():
                baseline_by_name = _parse_all_skill_eval_json(result.stdout)
                if skill_name in baseline_by_name:
                    baseline_mtime_by_path[path_key] = current_mtime
                    cache[cache_key] = baseline_by_name[skill_name]
                    return cache[cache_key]
        elif skill_name in baseline_by_name:
            baseline_mtime = baseline_mtime_by_path.get(path_key)
            if baseline_mtime is None:
                baseline_mtime_by_path[path_key] = current_mtime
                cache[cache_key] = baseline_by_name[skill_name]
                return cache[cache_key]
            if baseline_mtime == current_mtime:
                cache[cache_key] = baseline_by_name[skill_name]
                return cache[cache_key]

        # The target was edited after baseline ranking; re-run this skill only.
        if path_key in baseline_mtime_by_path and baseline_mtime_by_path[path_key] != current_mtime:
            baseline_mtime_by_path[path_key] = current_mtime

        result = subprocess.run(
            ["uv", "run", "--no-project", "python", str(script), "--skill", skill_name, "--format", "json"],
            cwd=str(root),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if result.returncode != 0 and not result.stdout.strip():
            return Evaluation(warnings=0, criticals=1, findings=[f"skill-eval failed for {skill_name}"])
        evaluation = _parse_skill_eval_json(result.stdout, skill_name)
        cache[cache_key] = evaluation
        return evaluation

    return evaluator


def default_evaluators(root: Path, skill_eval_script: Path | None = None) -> dict[str, Callable[[Path], Evaluation]]:
    return {
        "skill": make_skill_evaluator(root, skill_eval_script),
        "agent": evaluate_agent_target,
        "template": evaluate_template_target,
        "workflow-config": evaluate_workflow_config_target,
    }


def evaluate_target(target: Target, evaluators: dict[str, Callable[[Path], Evaluation]]) -> Evaluation:
    try:
        evaluator = evaluators[target.target_type]
    except KeyError as exc:
        raise ValueError(f"no evaluator registered for {target.target_type}") from exc
    return evaluator(target.path)


def default_candidate_provider(target: Target, before: Evaluation, time_budget: int = DEFAULT_TIME_BUDGET_SECONDS) -> str:
    if not shutil_which("claude"):
        raise CandidateUnavailable("claude CLI not available")

    findings = "\n".join(f"- {item}" for item in before.findings) or "- reduce evaluator warnings"
    current = target.path.read_text(encoding="utf-8")
    prompt = f"""You are improving a repository {target.target_type} asset.

Target path: {target.relative_path}
Fix only these evaluator findings:
{findings}

Rules:
- Make minimal, targeted edits.
- Do not change the asset's core purpose.
- Do not add unrelated sections or broad rewrites.
- Output only the complete updated file content, nothing else.

Current file:
{current}
"""
    result = subprocess.run(
        ["timeout", str(time_budget), "claude", "--print", "-p", prompt],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        raise CandidateUnavailable("claude CLI timed out or failed")
    if not result.stdout.strip():
        raise CandidateUnavailable("claude CLI returned empty content")
    return result.stdout


def shutil_which(command: str) -> str | None:
    for entry in os.environ.get("PATH", "").split(os.pathsep):
        candidate = Path(entry) / command
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return str(candidate)
    return None


def should_keep(before: Evaluation, after: Evaluation) -> tuple[bool, str]:
    if after.criticals > 0:
        return False, "revert-critical"
    if after.criticals < before.criticals:
        return True, "kept"
    if after.warnings < before.warnings:
        return True, "kept"
    return False, "revert-no-improve"


def append_result(results_file: Path, target: Target, before: Evaluation, after: Evaluation, result: str, duration_s: int) -> None:
    results_file.parent.mkdir(parents=True, exist_ok=True)
    row = {
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "target_type": target.target_type,
        "target_path": target.relative_path,
        "warnings_before": before.warnings,
        "warnings_after": after.warnings,
        "criticals_before": before.criticals,
        "criticals_after": after.criticals,
        "result": result,
        "duration_s": duration_s,
        "findings_before": before.findings,
        "findings_after": after.findings,
    }
    with results_file.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(row, sort_keys=True) + "\n")


def append_legacy_skill_result(tsv_file: Path, target: Target, before: Evaluation, after: Evaluation, result: str, duration_s: int) -> None:
    if target.target_type != "skill":
        return
    tsv_file.parent.mkdir(parents=True, exist_ok=True)
    if not tsv_file.exists():
        tsv_file.write_text("date\tskill\twarnings_before\twarnings_after\tresult\tduration_s\n", encoding="utf-8")
    row = "\t".join(
        [
            datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            skill_identifier(target.path),
            str(before.warnings),
            str(after.warnings),
            result,
            str(duration_s),
        ]
    )
    with tsv_file.open("a", encoding="utf-8") as stream:
        stream.write(row + "\n")


def run_attempt(
    target: Target,
    evaluator: Callable[[Path], Evaluation],
    candidate_provider: Callable[[Target, Evaluation], str],
    results_file: Path,
    commit_callback: Callable[[Path, str], None] | None,
    dry_run: bool,
    legacy_skill_results_tsv: Path | None = None,
) -> AttemptOutcome:
    start = time.time()
    before = evaluator(target.path)
    after = before

    if dry_run:
        outcome = AttemptOutcome(target, before, after, "dry-run", int(time.time() - start))
        append_result(results_file, target, before, after, outcome.result, outcome.duration_s)
        return outcome

    original = target.path.read_text(encoding="utf-8")
    try:
        candidate = candidate_provider(target, before)
    except CandidateUnavailable:
        outcome = AttemptOutcome(target, before, after, "no-candidate", int(time.time() - start))
        append_result(results_file, target, before, after, outcome.result, outcome.duration_s)
        if legacy_skill_results_tsv:
            append_legacy_skill_result(legacy_skill_results_tsv, target, before, after, outcome.result, outcome.duration_s)
        return outcome

    target.path.write_text(candidate, encoding="utf-8")
    after = evaluator(target.path)
    keep, result = should_keep(before, after)
    if keep:
        if commit_callback:
            commit_callback(target.path, f"autoresearch: improve {target.target_type} {target.relative_path}")
    else:
        target.path.write_text(original, encoding="utf-8")

    outcome = AttemptOutcome(target, before, after, result, int(time.time() - start))
    append_result(results_file, target, before, after, result, outcome.duration_s)
    if legacy_skill_results_tsv:
        append_legacy_skill_result(legacy_skill_results_tsv, target, before, after, result, outcome.duration_s)
    return outcome


def run_git(root: Path, args: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=check,
    )


def prepare_branch(root: Path, branch: str) -> tuple[str, bool]:
    original_branch = run_git(root, ["branch", "--show-current"]).stdout.strip()
    stashed = False
    if run_git(root, ["status", "--porcelain"], check=True).stdout.strip():
        print("WARNING: working tree not clean; stashing changes before autoresearch branch switch")
        run_git(root, ["stash", "push", "--include-untracked", "-m", f"autoresearch-pre-stash-{branch}"], check=False)
        stashed = True
    exists = run_git(root, ["rev-parse", "--verify", branch], check=False).returncode == 0
    if exists:
        run_git(root, ["switch", branch], check=False)
    else:
        result = run_git(root, ["switch", "-c", branch, "main"], check=False)
        if result.returncode != 0:
            run_git(root, ["checkout", "-b", branch, "main"], check=True)
    return original_branch, stashed


def restore_branch(root: Path, original_branch: str, stashed: bool) -> None:
    if original_branch:
        result = run_git(root, ["switch", original_branch], check=False)
        if result.returncode != 0:
            run_git(root, ["checkout", original_branch], check=False)
    if stashed:
        run_git(root, ["stash", "pop"], check=False)


def make_git_safe_commit_callback(root: Path) -> Callable[[Path, str], None]:
    lib = root / "scripts/cron/lib/git-safe.sh"

    def callback(path: Path, message: str) -> None:
        subprocess.run(
            [
                "bash",
                "-lc",
                (
                    f"source {json.dumps(str(lib))}; "
                    f"git_safe_init {json.dumps(str(root))}; "
                    f"git_safe_commit {json.dumps(message)} {json.dumps(str(path))}"
                ),
            ],
            cwd=str(root),
            check=True,
        )

    return callback


def select_candidates(
    targets: list[Target], evaluators: dict[str, Callable[[Path], Evaluation]], max_attempts: int
) -> list[tuple[Target, Evaluation]]:
    ranked: list[tuple[int, str, Target, Evaluation]] = []
    for target in targets:
        evaluation = evaluate_target(target, evaluators)
        if evaluation.issue_count > 0:
            ranked.append((evaluation.issue_count, target.relative_path, target, evaluation))
    ranked.sort(key=lambda item: (-item[0], item[1]))
    return [(target, evaluation) for _score, _name, target, evaluation in ranked[:max_attempts]]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run bounded autoresearch over repo ecosystem assets.")
    parser.add_argument("--root", default=None, help="Repository root. Defaults to git root.")
    parser.add_argument(
        "--target-type",
        choices=[*SUPPORTED_TARGET_TYPES, "all"],
        default="skill",
        help="Target type to evaluate.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Evaluate and report candidates without rewriting files.")
    parser.add_argument("--max-attempts", type=int, default=int(os.environ.get("MAX_ATTEMPTS", "5")))
    parser.add_argument("--time-budget", type=int, default=DEFAULT_TIME_BUDGET_SECONDS)
    parser.add_argument("--branch", default=None, help="Autoresearch branch name.")
    parser.add_argument("--no-branch", action="store_true", help="Do not create/switch branches before applying changes.")
    parser.add_argument("--results-file", default=None, help="JSONL result artifact path.")
    parser.add_argument("--legacy-skill-results-tsv", default=None, help="Optional legacy skill TSV result artifact.")
    parser.add_argument("--skill-eval-script", default=None, help="Optional skill-eval script path.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    root = Path(args.root).resolve() if args.root else git_root(Path.cwd())
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    branch = args.branch or ("autoresearch/skills-" + date if args.target_type == "skill" else "autoresearch/repo-ecosystem-" + date)
    results_file = Path(args.results_file) if args.results_file else root / DEFAULT_RESULTS_FILE
    if not results_file.is_absolute():
        results_file = root / results_file
    legacy_tsv = Path(args.legacy_skill_results_tsv) if args.legacy_skill_results_tsv else None
    if legacy_tsv is not None and not legacy_tsv.is_absolute():
        legacy_tsv = root / legacy_tsv
    skill_eval_script = Path(args.skill_eval_script) if args.skill_eval_script else None
    if skill_eval_script is not None and not skill_eval_script.is_absolute():
        skill_eval_script = root / skill_eval_script

    target_types = list(SUPPORTED_TARGET_TYPES) if args.target_type == "all" else [args.target_type]
    evaluators = default_evaluators(root, skill_eval_script)

    print(f"=== [repo-ecosystem-autoresearch] Starting {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')} ===")
    print(f"  Branch: {branch}")
    print(f"  Target type: {args.target_type}")
    print(f"  Max attempts: {args.max_attempts}")
    print(f"  Dry run: {args.dry_run}")
    print(f"  Results: {target_path_for_results(results_file, root)}")

    original_branch = ""
    stashed = False
    if not args.dry_run and not args.no_branch:
        original_branch, stashed = prepare_branch(root, branch)

    try:
        commit_callback = None if args.dry_run else make_git_safe_commit_callback(root)
        for target_type in target_types:
            targets = discover_targets(root, target_type)
            candidates = select_candidates(targets, evaluators, args.max_attempts)
            print(f"--- {target_type}: {len(candidates)} candidate(s) from {len(targets)} target(s) ---")
            if args.dry_run:
                print(f"Dry run: no changes made for {target_type}")
                for target, evaluation in candidates:
                    print(f"  {target.relative_path} ({evaluation.issue_count} issue(s))")
                continue
            for target, _evaluation in candidates:
                provider = lambda current_target, before: default_candidate_provider(
                    current_target, before, time_budget=args.time_budget
                )
                outcome = run_attempt(
                    target,
                    evaluator=evaluators[target.target_type],
                    candidate_provider=provider,
                    results_file=results_file,
                    commit_callback=commit_callback,
                    dry_run=False,
                    legacy_skill_results_tsv=legacy_tsv,
                )
                print(
                    f"  {outcome.result}: {target.relative_path} "
                    f"warnings {outcome.before.warnings}->{outcome.after.warnings}, "
                    f"criticals {outcome.before.criticals}->{outcome.after.criticals}"
                )
    finally:
        if original_branch:
            restore_branch(root, original_branch, stashed)

    print("=== [repo-ecosystem-autoresearch] Done ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
