"""Synthetic acceptance tests: no client records, apps, solvers or downloads."""
import copy
import json
import os
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
    def init_owner(self, root):
        env = patch.dict(os.environ)
        env.start()
        self.addCleanup(env.stop)
        for name in ("GIT_DIR", "GIT_COMMON_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE",
                     "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES"):
            os.environ.pop(name, None)
        self.git(root, "init", "-q")
        self.git(root, "remote", "add", "origin", "https://github.com/example/private-owner.git")
        source = root / "client.json"
        source.write_text(json.dumps(record()), encoding="utf-8")
        return source

    @staticmethod
    def git(root, *args):
        subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True,
                       creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))

    def commit_record(self, source, data):
        source.write_text(json.dumps(data), encoding="utf-8")
        self.git(source.parent, "add", source.name)
        self.git(source.parent, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "-c", "commit.gpgsign=false", "commit", "-qm", "Synthetic record")

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
        valid = json.dumps(record())
        self.assertEqual(hp.parse_record(valid), record())
        duplicate = valid.replace('"schema": 1', '"schema": 1, "schema": 1', 1)
        with self.assertRaisesRegex(ValueError, "^Duplicate JSON field$"):
            hp.parse_record(duplicate)
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
        with tempfile.TemporaryDirectory() as tmp:
            owner = Path(tmp)
            source = self.init_owner(owner)
            for held in (False, True):
                with self.subTest(hold=held):
                    data = dict(record(), hold=held)
                    self.commit_record(source, data)
                    out = owner / str(held)
                    hp.write_bundle(data, out, hp.owner_receipt(source, owner, data))
                    self.assertEqual(hp.verify_bundle(out)["hold"], held)
                    if held:
                        with self.assertRaisesRegex(ValueError, "Hold"):
                            hp.verify_bundle(out, for_publication=True, owner_root=owner)
                    else:
                        self.assertFalse(hp.verify_bundle(out, for_publication=True, owner_root=owner)["hold"])

    def test_publication_requires_receipt_for_present_pdf(self):
        with tempfile.TemporaryDirectory() as tmp:
            owner = Path(tmp)
            source = self.init_owner(owner)
            data = record()
            self.commit_record(source, data)
            out = owner / "bundle"
            hp.write_bundle(data, out, hp.owner_receipt(source, owner, data))
            (out / "dashboard.pdf").write_bytes(b"%PDF-fixture")
            with self.assertRaisesRegex(ValueError, "PDF receipt"):
                hp.verify_bundle(out, for_publication=True, owner_root=owner)

    def test_pdf_and_receipt_type_and_size_checked_before_read(self):
        for name, limit in (("dashboard.pdf", 32 * 1024 * 1024), ("pdf-receipt.json", hp.LIMIT)):
            for invalid in ("directory", "oversized", "empty"):
                with self.subTest(name=name, invalid=invalid), tempfile.TemporaryDirectory() as tmp:
                    out = Path(tmp) / "bundle"
                    hp.write_bundle(record(), out)
                    pdf, receipt = out / "dashboard.pdf", out / "pdf-receipt.json"
                    bad = out / name
                    (receipt if bad == pdf else pdf).write_bytes(b"fixture")
                    if invalid == "directory":
                        bad.mkdir()
                    else:
                        with bad.open("wb") as stream:
                            stream.truncate(limit + 1 if invalid == "oversized" else 0)
                    regular_open = Path.open

                    def check_before_read(path, *args, **kwargs):
                        if path in (pdf, receipt):
                            self.fail(f"Read {path.name} before checking {name}")
                        return regular_open(path, *args, **kwargs)

                    with patch.object(Path, "open", check_before_read), self.assertRaises(ValueError):
                        hp.verify_bundle(out, for_publication=True)

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
            owner = Path(tmp)
            source = self.init_owner(owner)
            with self.assertRaises(ValueError):
                hp.owner_receipt(source, owner, record())
            self.commit_record(source, record())
            receipt = hp.owner_receipt(source, owner, record())
            self.assertEqual(receipt["disposition"], "committed")
            self.assertEqual(len(receipt["commit"]), 40)
            dirty = dict(record(), title="Dirty")
            source.write_text(json.dumps(dirty), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Canonical record is dirty"):
                hp.owner_receipt(source, owner, dirty)

    def test_owner_origin_requires_https_or_ssh(self):
        with tempfile.TemporaryDirectory() as tmp:
            owner = Path(tmp)
            source = self.init_owner(owner)
            self.commit_record(source, record())
            for origin in ("https://github.com/", "ssh://git@github.com/", "git@github.com:",
                           "http://github.com/", "git://github.com/", "file://github.com/"):
                with self.subTest(origin=origin):
                    self.git(owner, "remote", "set-url", "origin", origin + "example/private-owner.git")
                    if origin.startswith(("https:", "ssh:", "git@")):
                        self.assertEqual(hp.owner_receipt(source, owner, record())["repository"],
                                         "example/private-owner")
                    else:
                        with self.assertRaisesRegex(ValueError, "Owner origin"):
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
