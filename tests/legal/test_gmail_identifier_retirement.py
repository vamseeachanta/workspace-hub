"""Exercise synthetic mail only; never load host overlays or Gmail credentials."""
import ast
import contextlib
import io
from pathlib import Path
import tempfile
import types
import unittest
from unittest import mock


SCRIPT = Path(__file__).resolve().parents[2] / "scripts/email/gmail-archive-extract.py"


def load_functions():
    tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
    tree.body = [node for node in tree.body
                 if isinstance(node, (ast.Import, ast.ImportFrom, ast.FunctionDef))]
    module = types.ModuleType("synthetic_gmail")
    exec(compile(tree, str(SCRIPT), "exec"), module.__dict__)
    module.ACCOUNTS = {"ace": {"email": "synthetic@example.invalid"}}
    module.DENY_PATH = Path("unused-test-denylist")
    return module


class GmailIdentifierRetirement(unittest.TestCase):
    def test_named_mail_archives_and_deletion_remains_explicit(self):
        for flags, saved, deleted in (([], True, False), (["--delete"], True, True),
                                      (["--dry-run", "--delete"], False, False)):
            with self.subTest(flags=flags), tempfile.TemporaryDirectory() as temp:
                module = load_functions()
                module.ACE_BASE = Path(temp)
                detail = {"payload": {"headers": [
                    {"name": "From", "value": "sender@example.invalid"},
                    {"name": "Subject", "value": "Synthetic Client identifier"}]}}
                replacements = {
                    "overlay_gate": mock.Mock(), "load_routing": mock.Mock(return_value={"default": "synthetic/docs/email"}),
                    "refresh_token": mock.Mock(return_value="synthetic-token"),
                    "gmail_search": mock.Mock(return_value={"messages": [{"id": "test-id"}]}),
                    "gmail_full": mock.Mock(return_value=detail),
                    "gmail_delete": mock.Mock(), "gmail_get_attachment": mock.Mock(side_effect=AssertionError("no attachment expected")),
                    "extract_text_body": mock.Mock(return_value="Synthetic Client body"),
                    "git_commit": mock.Mock(return_value="mocked commit"),
                    "legal_scan": mock.Mock(return_value=[("Synthetic Client", "identifier")]),
                }
                with mock.patch.dict(module.__dict__, replacements), \
                     mock.patch.object(module.sys, "argv", [str(SCRIPT), "--account", "ace", *flags]), \
                     mock.patch.object(module.time, "sleep"), contextlib.redirect_stdout(io.StringIO()):
                    module.main()
                files = list(Path(temp).rglob("*.md"))
                self.assertEqual(bool(files), saved)
                self.assertEqual(replacements["gmail_delete"].called, deleted)
                self.assertEqual(replacements["git_commit"].called, saved)
                replacements["legal_scan"].assert_not_called()
                if files:
                    self.assertIn("Synthetic Client body", files[0].read_text(encoding="utf-8"))

    def test_missing_private_overlay_stops_before_credentials_or_network(self):
        module = load_functions()
        class Absent(Exception):
            pass
        overlay = types.SimpleNamespace(PrivateOverlayAbsent=Absent,
            require_present=mock.Mock(side_effect=Absent("not configured")))
        with mock.patch.object(module, "_private_overlay", return_value=overlay), \
             mock.patch.object(module, "refresh_token") as refresh, \
             mock.patch.object(module.sys, "argv", [str(SCRIPT), "--account", "ace", "--delete", "--force"]), \
             contextlib.redirect_stderr(io.StringIO()) as output, self.assertRaises(SystemExit) as error:
            module.main()
        self.assertEqual(error.exception.code, 2)
        self.assertIn("--force is ignored", output.getvalue())
        refresh.assert_not_called()


if __name__ == "__main__":
    unittest.main()
