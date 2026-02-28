#!/usr/bin/env python3
"""Convert provider-specific JSON review output into the shared markdown schema."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


REQUIRED_KEYS = (
    "verdict",
    "summary",
    "issues_found",
    "suggestions",
    "questions_for_author",
)
VALID_VERDICTS = frozenset(("APPROVE", "REQUEST_CHANGES", "REJECT"))


def _extract_json_blob(text: str) -> dict:
    decoder = json.JSONDecoder()
    fenced_blocks = re.findall(r"```(?:json)?\s*\n?(.*?)\s*```", text, re.DOTALL)
    for block in fenced_blocks:
        inner = block.strip()
        start = inner.find("{")
        if start == -1:
            continue
        try:
            payload, _ = decoder.raw_decode(inner[start:])
            if not isinstance(payload, dict):
                continue
            return payload
        except json.JSONDecodeError:
            continue

    pos = 0
    while True:
        start = text.find("{", pos)
        if start == -1:
            raise ValueError("No JSON object found in provider output")
        try:
            payload, _ = decoder.raw_decode(text[start:])
            if not isinstance(payload, dict):
                pos = start + 1
                continue
            return payload
        except json.JSONDecodeError:
            pos = start + 1


def _coerce_review(payload: dict) -> dict:
    if not isinstance(payload, dict):
        raise ValueError(f"Expected a JSON object, got {type(payload).__name__}")

    review = {}
    for key in REQUIRED_KEYS:
        if key not in payload:
            raise ValueError(f"Missing required key: {key}")
        value = payload[key]
        if key in {"issues_found", "suggestions", "questions_for_author"}:
            if isinstance(value, str):
                cleaned = value.strip()
                review[key] = [cleaned] if cleaned else []
            elif isinstance(value, list):
                cleaned_values = []
                for item in value:
                    if item is None:
                        continue
                    if not isinstance(item, str):
                        raise ValueError(f"Invalid list item type for {key}: {type(item).__name__}")
                    cleaned = item.strip()
                    if cleaned:
                        cleaned_values.append(cleaned)
                review[key] = cleaned_values
            else:
                raise ValueError(f"Invalid list value for {key}")
        else:
            review[key] = str(value).strip()
            if not review[key]:
                raise ValueError(f"Empty value for {key}")
            if key == "verdict" and review[key] not in VALID_VERDICTS:
                raise ValueError(f"Invalid verdict: {review[key]}")
    return review


def _parse_claude(text: str) -> dict:
    payload = _extract_json_blob(text)
    if isinstance(payload.get("structured_output"), dict):
        return _coerce_review(payload["structured_output"])
    if isinstance(payload.get("result"), str) and payload["result"].strip():
        return _coerce_review(_extract_json_blob(payload["result"]))
    return _coerce_review(payload)


def _parse_gemini(text: str) -> dict:
    payload = _extract_json_blob(text)
    if isinstance(payload.get("response"), str):
        return _coerce_review(_extract_json_blob(payload["response"]))
    return _coerce_review(payload)


def _render_markdown(review: dict) -> str:
    def render_list(values: list[str]) -> str:
        if not values:
            return "- None.\n"
        return "".join(f"- {value}\n" for value in values)

    return (
        f"### Verdict: {review['verdict']}\n\n"
        "### Summary\n"
        f"{review['summary']}\n\n"
        "### Issues Found\n"
        f"{render_list(review['issues_found'])}\n"
        "### Suggestions\n"
        f"{render_list(review['suggestions'])}\n"
        "### Questions for Author\n"
        f"{render_list(review['questions_for_author'])}"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", choices=("claude", "gemini", "codex"), required=True)
    parser.add_argument("--input", required=True)
    args = parser.parse_args()

    try:
        text = Path(args.input).read_text(encoding="utf-8")
        if args.provider == "claude":
            review = _parse_claude(text)
        elif args.provider == "gemini":
            review = _parse_gemini(text)
        else:
            review = _coerce_review(_extract_json_blob(text))
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1

    sys.stdout.write(_render_markdown(review))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
