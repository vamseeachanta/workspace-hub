#!/usr/bin/env python3
"""Local owner-board JSON sync for decision issues and PRs.

The script only reads/writes GitHub issue state through ``gh``. It does not
connect to the owner board database; the coordinator imports the JSON files.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


BOARD_FILES = ("cards.json", "decisions.json", "goals.json", "sessions.json", "subgoals.json")
DEFAULT_OPTIONS = [
    {"id": "approve", "label": "Proceed", "dispatch_label": "dispatch:ready"},
    {"id": "defer", "label": "Keep blocked", "dispatch_label": "dispatch:blocked"},
    {"id": "drop", "label": "Drop", "dispatch_label": "dispatch:done"},
]


def gh_json(args: list[str]) -> Any:
    result = subprocess.run(["gh", *args], text=True, capture_output=True, check=True)
    text = result.stdout.strip()
    return json.loads(text) if text else None


def gh(args: list[str]) -> str:
    result = subprocess.run(["gh", *args], text=True, capture_output=True, check=True)
    return result.stdout.strip()


def labels(item: dict[str, Any]) -> list[str]:
    names = []
    for label in item.get("labels") or []:
        names.append(label.get("name") if isinstance(label, dict) else str(label))
    return [name for name in names if name]


def first_label(item: dict[str, Any], prefix: str) -> str | None:
    return next((name for name in labels(item) if name.startswith(prefix)), None)


def issue_ref(repo: str, kind: str, number: int) -> str:
    return f"{repo.split('/')[-1]}-{kind}-{number}"


def extract_issue_number(text: str, marker: str) -> int | None:
    match = re.search(rf"{re.escape(marker)}:\s*#(\d+)", text, re.IGNORECASE)
    return int(match.group(1)) if match else None


def extract_tier(text: str, label_names: list[str]) -> str | None:
    for name in label_names:
        if name.startswith("tier:"):
            return name.split(":", 1)[1].upper()
    match = re.search(r"\bTier\s+([ABC])\b", text, re.IGNORECASE)
    return match.group(1).upper() if match else None


def extract_done_when(text: str) -> str:
    match = re.search(r"\*\*Done when:\*\*\s*(.+?)(?:\n\n|\Z)", text, re.IGNORECASE | re.DOTALL)
    if not match:
        return ""
    return " ".join(match.group(1).split())


def recommended_choice(label_names: list[str]) -> str:
    dispatch = next((name for name in label_names if name.startswith("dispatch:")), "")
    if dispatch.endswith("blocked"):
        return "defer"
    if dispatch.endswith("done"):
        return "drop"
    return "approve"


def make_goal_id(repo: str, item: dict[str, Any]) -> str | None:
    body = item.get("body") or ""
    number = extract_issue_number(body, "Parent RFC") or extract_issue_number(body, "Epic")
    if not number:
        return None
    return f"{repo.split('/')[-1]}-{number}"


def make_card(repo: str, kind: str, item: dict[str, Any]) -> dict[str, Any]:
    label_names = labels(item)
    decision_label = first_label(item, "decision:") or "decision:unknown"
    number = int(item["number"])
    rec = recommended_choice(label_names)
    body = item.get("body") or ""
    return {
        "id": issue_ref(repo, kind, number),
        "section": decision_label,
        "order": number,
        "title": item.get("title") or "",
        "repo": repo,
        "issue": number,
        "url": item.get("url") or "",
        "category": decision_label,
        "configs": {"source": "github", "kind": kind, "labels": label_names},
        "question": item.get("title") or "",
        "impact": extract_done_when(body) or f"Tier {extract_tier(body, label_names) or 'unknown'} decision.",
        "recommendation": rec,
        "recommended": rec,
        "options": DEFAULT_OPTIONS,
        "urgent": any(name in {"urgent", "priority:p0", "priority:P0"} for name in label_names),
        "goal": make_goal_id(repo, item),
        "owner_answer": None,
        "answered_at": None,
    }


def make_subgoal(repo: str, kind: str, item: dict[str, Any]) -> dict[str, Any]:
    label_names = labels(item)
    number = int(item["number"])
    body = item.get("body") or ""
    return {
        "id": issue_ref(repo, kind, number),
        "goal_id": make_goal_id(repo, item),
        "issue": number,
        "repo": repo,
        "tier": extract_tier(body, label_names),
        "lane": first_label(item, "lane:"),
        "dispatch": first_label(item, "dispatch:"),
        "done_when": extract_done_when(body),
        "progress": item.get("state") or "OPEN",
    }


def list_repo_labels(repo: str, prefix: str) -> list[str]:
    data = gh_json(["label", "list", "--repo", repo, "--search", prefix, "--limit", "1000", "--json", "name"]) or []
    return sorted({item["name"] for item in data if item.get("name", "").startswith(prefix)})


def list_items(repo: str, kind: str, label: str) -> list[dict[str, Any]]:
    command = kind if kind == "issue" else "pr"
    return gh_json(
        [
            command,
            "list",
            "--repo",
            repo,
            "--state",
            "open",
            "--limit",
            "1000",
            "--label",
            label,
            "--json",
            "number,title,body,labels,url,state",
        ]
    ) or []


def export_board(repos: list[str], out_dir: Path) -> None:
    cards: list[dict[str, Any]] = []
    subgoals: list[dict[str, Any]] = []
    goals: dict[str, dict[str, Any]] = {}
    for repo in repos:
        seen_cards: set[tuple[str, int]] = set()
        seen_subgoals: set[tuple[str, int]] = set()
        decision_labels = list_repo_labels(repo, "decision:")
        lane_labels = list_repo_labels(repo, "lane:")
        for kind in ("issue", "pr"):
            for decision_label in decision_labels:
                for item in list_items(repo, kind, decision_label):
                    key = (kind, int(item["number"]))
                    if key in seen_cards:
                        continue
                    seen_cards.add(key)
                    card = make_card(repo, kind, item)
                    cards.append(card)
                    if card["goal"]:
                        goals[card["goal"]] = goal_record(card["goal"], repo)
            for lane_label in lane_labels:
                for item in list_items(repo, kind, lane_label):
                    key = (kind, int(item["number"]))
                    if key in seen_subgoals:
                        continue
                    seen_subgoals.add(key)
                    subgoal = make_subgoal(repo, kind, item)
                    subgoals.append(subgoal)
                    if subgoal["goal_id"]:
                        goals[subgoal["goal_id"]] = goal_record(subgoal["goal_id"], repo)
    cards.sort(key=lambda c: (c["section"], c["repo"], c["configs"]["kind"] != "issue", c["order"]))
    subgoals.sort(key=lambda s: (s["repo"], s["issue"]))
    write_json(out_dir, "cards.json", cards)
    write_json(out_dir, "decisions.json", [decision_stub(card) for card in cards])
    write_json(out_dir, "goals.json", sorted(goals.values(), key=lambda g: g["id"]))
    write_json(out_dir, "sessions.json", [])
    write_json(out_dir, "subgoals.json", subgoals)


def goal_record(goal_id: str, repo: str) -> dict[str, Any]:
    number = int(goal_id.rsplit("-", 1)[1])
    return {"id": goal_id, "title": f"Issue #{number}", "issue": number, "repo": repo, "status": "open"}


def decision_stub(card: dict[str, Any]) -> dict[str, Any]:
    return {
        "card_id": card["id"],
        "repo": card["repo"],
        "issue": card["issue"],
        "answer": None,
        "written_back": False,
        "comment_url": None,
    }


def write_json(out_dir: Path, name: str, data: Any) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / name
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    loaded = json.loads(path.read_text(encoding="utf-8"))
    if loaded != data:
        raise RuntimeError(f"read-back verification failed for {path}")


def load_decision_payload(path: Path) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        return payload, {}
    if not isinstance(payload, dict):
        raise ValueError("decisions file must contain a list or object")
    cards = {card.get("id"): card for card in payload.get("cards", []) if isinstance(card, dict)}
    decisions = payload.get("decisions", [])
    return decisions, cards


def decision_id(decision: dict[str, Any]) -> str:
    value = decision.get("id") or decision.get("card_id")
    if not value:
        raise ValueError(f"decision lacks id/card_id: {decision}")
    return str(value)


def decision_answer(decision: dict[str, Any]) -> str | None:
    value = decision.get("choice") or decision.get("answer") or decision.get("owner_answer")
    return str(value) if value not in (None, "") else None


def target_label(decision: dict[str, Any], answer: str) -> str:
    for key in ("label", "target_label", "dispatch_label", "implied_label"):
        if decision.get(key):
            return str(decision[key])
    implied = {"approve": "dispatch:ready", "defer": "dispatch:blocked", "drop": "dispatch:done"}
    return implied.get(answer.lower(), "dispatch:ready")


def decision_repo_issue(decision: dict[str, Any], cards: dict[str, dict[str, Any]]) -> tuple[str, int]:
    card = cards.get(str(decision.get("card_id") or decision.get("id")), {})
    repo = decision.get("repo") or card.get("repo")
    issue = decision.get("issue") or decision.get("number") or card.get("issue")
    if not repo or not issue:
        raise ValueError(f"decision lacks repo/issue: {decision}")
    return str(repo), int(issue)


def already_written(repo: str, issue: int, decision_key: str) -> tuple[bool, list[str]]:
    data = gh_json(["issue", "view", str(issue), "--repo", repo, "--json", "labels,comments"]) or {}
    comments = data.get("comments") or []
    marker = f"Owner decision {decision_key}:"
    seen = any(marker in (comment.get("body") or "") for comment in comments)
    return seen, labels(data)


def import_decisions(path: Path, apply: bool) -> None:
    decisions, cards = load_decision_payload(path)
    for decision in decisions:
        if decision.get("written_back"):
            continue
        key = decision_id(decision)
        answer = decision_answer(decision)
        if not answer:
            continue
        repo, issue = decision_repo_issue(decision, cards)
        label = target_label(decision, answer)
        note = str(decision.get("note") or "").strip()
        body = f"Owner decision {key}: {answer}" + (f" (+ {note})" if note else "")
        if not apply:
            print(f"DRY-RUN {repo}#{issue}: comment={body!r} add={label}")
            continue
        seen, label_names = already_written(repo, issue, key)
        if seen:
            print(f"SKIP {repo}#{issue}: Owner decision {key} already written")
            continue
        for name in label_names:
            if name.startswith(("decision:", "dispatch:")):
                gh(["issue", "edit", str(issue), "--repo", repo, "--remove-label", name])
        gh(["issue", "edit", str(issue), "--repo", repo, "--add-label", label])
        comment_url = gh(["issue", "comment", str(issue), "--repo", repo, "--body", body])
        print(f"WROTE {repo}#{issue}: {comment_url}")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    export = sub.add_parser("export", help="write owner-board JSON files from GitHub issues/PRs")
    export.add_argument("--repo", action="append", dest="repos", required=True)
    export.add_argument("--out-dir", type=Path, required=True)
    imp = sub.add_parser("import", help="write owner board decisions back to GitHub")
    imp.add_argument("--decisions", type=Path, required=True)
    imp.add_argument("--apply", action="store_true", help="perform GitHub writes; default is dry-run")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    if args.command == "export":
        export_board(args.repos, args.out_dir)
    else:
        import_decisions(args.decisions, args.apply)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
