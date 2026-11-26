"""Synthetic acceptance tests: no client records, apps, solvers or downloads."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.client_llm_wiki import home_projection as hp


def record():
    return {
        "schema": 1, "client": "example", "owner_repository": "example/private-owner",
        "title": "Weekly review", "checked_at": "2026-10-06T16:00:00Z",
        "coverage": ["Selected records; not complete correspondence."],
        "hold": False,
        "sections": [
            {"id": "weekly", "title": "Weekly focus", "items": [
                {"text": "Review the draft. Owner: Example Reviewer.", "links": []}]},
            {"id": "rolling", "title": "Rolling last 30 days", "items": [
                {"text": "5 October: Draft entered review.", "links": [
                    {"label": "Project context", "url": "https://example.com/context"}]}]},
        ],
        "common_resources": {"label": "Engineering Commons", "url": "https://example.com/commons"},
    }


class ProjectionTests(unittest.TestCase):
    def test_same_model_in_markdown_html_and_index(self):
        data = record()
        rendered = hp.render(data)
        self.assertEqual(rendered["dashboard.html"], rendered["index.html"])
        version = hp.content_version(data)
        self.assertIn(version, rendered["space.md"])
        self.assertIn(version, rendered["dashboard.html"])
        self.assertIn("Review the draft.", rendered["space.md"])
        self.assertIn("Review the draft.", rendered["dashboard.html"])
        self.assertLess(rendered["space.md"].index("Rolling last 30 days"), rendered["space.md"].index("Common engineering resources"))

    def test_content_change_invalidates_version(self):
        data = record()
        changed = copy.deepcopy(data)
        changed["sections"][0]["items"][0]["text"] = "Changed owner"
        self.assertNotEqual(hp.content_version(data), hp.content_version(changed))

    def test_duplicate_and_unknown_fields_rejected(self):
        with self.assertRaises(ValueError):
            hp.parse_record('{"schema":1,"schema":1}')
        data = record()
        data["unexpected"] = True
        with self.assertRaises(ValueError):
            hp.validate_record(data)

    def test_invalid_ids_duplicate_sections_and_empty_record(self):
        for change in ("duplicate", "traversal", "empty", "wrong_bool"):
            with self.subTest(change=change):
                data = record()
                if change == "duplicate":
                    data["sections"][1]["id"] = "weekly"
                elif change == "traversal":
                    data["sections"][0]["id"] = "../../escape"
                elif change == "empty":
                    data["sections"] = []
                else:
                    data["hold"] = "false"
                with self.assertRaises(ValueError):
                    hp.validate_record(data)

    def test_unsafe_links_rejected_and_markup_escaped(self):
        for url in ("javascript:alert(1)", "data:text/html,hi", "//example.com/x", "https://example.com/\nX"):
            data = record()
            data["common_resources"]["url"] = url
            with self.assertRaises(ValueError):
                hp.render(data)
        data = record()
        data["sections"][0]["items"][0]["text"] = "<script>alert(1)</script> [link] *text*"
        out = hp.render(data)
        self.assertNotIn("<script>alert(1)</script>", out["dashboard.html"])
        self.assertIn("&lt;script&gt;", out["dashboard.html"])
        self.assertIn(r"\[link\]", out["space.md"])

    def test_new_destination_only_and_no_partial_acceptance(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "bundle"
            hp.write_bundle(record(), out)
            before = {p.name: p.read_bytes() for p in out.iterdir()}
            with self.assertRaises(FileExistsError):
                hp.write_bundle(record(), out)
            self.assertEqual(before, {p.name: p.read_bytes() for p in out.iterdir()})
            hp.verify_bundle(out)
            (out / "space.md").write_text("tampered", encoding="utf-8")
            with self.assertRaises(ValueError):
                hp.verify_bundle(out)

    def test_hold_blocks_all_publication_acceptance(self):
        data = record()
        data["hold"] = True
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "held"
            hp.write_bundle(data, out)
            with self.assertRaises(ValueError):
                hp.verify_bundle(out, for_publication=True)
            self.assertTrue(hp.verify_bundle(out)["hold"])

    def test_feedback_bound_to_version_and_section(self):
        data = record()
        feedback = {
            "schema": 1, "content_version": hp.content_version(data),
            "section_id": "weekly", "comment": "<img src=x>", "decision": "Proposed",
        }
        proposal = hp.feedback_proposal(data, feedback)
        self.assertEqual(proposal["status"], "proposed")
        self.assertEqual(proposal["comment"], "<img src=x>")
        self.assertEqual(data, record())
        for field, value in (("content_version", "stale"), ("section_id", "unknown"), ("schema", True)):
            bad = dict(feedback, **{field: value})
            with self.assertRaises(ValueError):
                hp.feedback_proposal(data, bad)

    def test_feedback_size_unknown_fields_and_type_rejected(self):
        data = record()
        base = {"schema": 1, "content_version": hp.content_version(data),
                "section_id": "weekly", "comment": "x", "decision": ""}
        for extra in ({"comment": "x" * 4001}, {"comment": {}}, {"evil": True}):
            with self.assertRaises(ValueError):
                hp.feedback_proposal(data, dict(base, **extra))

    def test_owner_binding_requires_committed_matching_record(self):
        with tempfile.TemporaryDirectory() as tmp:
            owner = Path(tmp) / "owner"
            owner.mkdir()
            subprocess.run(["git", "init", "-q", str(owner)], check=True)
            subprocess.run(["git", "-C", str(owner), "remote", "add", "origin", "https://github.com/example/private-owner.git"], check=True)
            source = owner / "client.json"
            source.write_text(json.dumps(record()), encoding="utf-8")
            with self.assertRaises(ValueError):
                hp.owner_receipt(source, owner, record())
            subprocess.run(["git", "-C", str(owner), "add", "client.json"], check=True)
            subprocess.run(["git", "-C", str(owner), "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "commit", "-qm", "Synthetic record"], check=True)
            receipt = hp.owner_receipt(source, owner, record())
            self.assertEqual(receipt["disposition"], "committed")
            self.assertEqual(len(receipt["commit"]), 40)
            source.write_text(json.dumps(dict(record(), title="Dirty")), encoding="utf-8")
            with self.assertRaises(ValueError):
                hp.owner_receipt(source, owner, record())

    def test_feedback_output_cannot_escape_owner(self):
        with tempfile.TemporaryDirectory() as tmp:
            owner = Path(tmp) / "private"
            owner.mkdir()
            self.assertEqual(hp.owner_destination(owner / "feedback.json", owner), owner / "feedback.json")
            for out in (Path(tmp) / "shared" / "feedback.json", owner / ".." / "shared.json", owner / ".git" / "config"):
                with self.subTest(out=out):
                    with self.assertRaises(ValueError):
                        hp.owner_destination(out, owner)

    def test_pdf_content_and_link_targets_are_rechecked(self):
        data = record()
        data["common_resources"]["url"] = "https://example.com/a%2Fb%3Fc"
        text = " ".join(line + " " + " ".join(link["label"] for link in links)
                        for _, _, line, links in hp._model(data))
        urls = [link["url"] for _, _, _, links in hp._model(data) for link in links]
        class Annotation:
            def __init__(self, url):
                self.url = url
            def get_object(self):
                return {"/A": {"/URI": self.url}}
        class Page:
            def __init__(self):
                self.text = text
                self.links = urls
            def extract_text(self):
                return self.text
            def get(self, key, default=None):
                return [Annotation(url) for url in self.links] if key == "/Annots" else default
        page = Page()
        reader = SimpleNamespace(pages=[page])
        with tempfile.TemporaryDirectory() as tmp, patch.dict(sys.modules, {"pypdf": SimpleNamespace(PdfReader=lambda path: reader)}):
            out = Path(tmp) / "bundle"
            hp.write_bundle(data, out)
            (out / "dashboard.pdf").write_bytes(b"%PDF-1.7 synthetic-reader-fixture")
            receipt = hp.record_pdf(out)
            self.assertTrue(receipt["links_checked"])
            self.assertEqual(hp.verify_bundle(out)["pdf_status"], "generated_and_checked")
            page.links = [url.replace("a%2Fb%3Fc", "a/b?c") for url in urls]
            with self.assertRaises(ValueError):
                hp.verify_bundle(out)
            page.links = ["https://example.com/wrong-target"]
            with self.assertRaises(ValueError):
                hp.verify_bundle(out)
            page.links = urls
            page.text = "Missing canonical content"
            with self.assertRaises(ValueError):
                hp.verify_bundle(out)


if __name__ == "__main__":
    unittest.main()
