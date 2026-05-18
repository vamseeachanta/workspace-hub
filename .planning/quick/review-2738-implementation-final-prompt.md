# Final adversarial implementation re-review — issue #2738

Review only this repo-side diff for the approved Telegram/Hermes coordinator hardening artifact. Prior review found MINOR: stale HTML test count and env-key whitespace bypass. Both were patched.

Validation now run:
- `uv run pytest tests/readiness/test_telegram_hermes_readiness.py -q` => 39 passed
- `bash -n scripts/operations/verify-hermes-gateway-coordinator.sh && shellcheck scripts/operations/verify-hermes-gateway-coordinator.sh` => pass/no output
- `git diff --check -- scripts/operations/verify-hermes-gateway-coordinator.sh tests/readiness/test_telegram_hermes_readiness.py docs/ops/telegram-hermes-coordinator/implementation-notes.html` => pass/no output
- host safe probe still correctly fails closed: 7 passed, 4 failed (allow-all users, env wiring, TimeoutStopUSec, duplicate polling conflict). The issue should land repo-side verifier/docs/tests and leave host dispatch blocked.

Questions:
1. Any MAJOR blocker in this diff before commit?
2. Are the two prior MINOR items fixed?
3. Does it preserve secret redaction and truthful blocked host status?

Required output: Verdict APPROVE/MINOR/MAJOR, findings only.

```diff
diff --git a/tests/readiness/test_telegram_hermes_readiness.py b/tests/readiness/test_telegram_hermes_readiness.py
index 0a0fa3b3c..b944d648f 100644
--- a/tests/readiness/test_telegram_hermes_readiness.py
+++ b/tests/readiness/test_telegram_hermes_readiness.py
@@ -900,6 +900,50 @@ def test_coordinator_verifier_redacts_env_values(tmp_path: Path) -> None:
     assert "67890" not in result.stdout


+def test_coordinator_verifier_rejects_optional_environment_file(tmp_path: Path) -> None:
+    env_file, env = _coordinator_env(tmp_path)
+    _write_fake_command(
+        Path(env["PATH"].split(":", 1)[0]),
+        "systemctl",
+        f"""
+if [[ "$1" == "is-active" ]]; then echo active; exit 0; fi
+if [[ "$1" == "show" ]]; then
+  prop="${{4:-${{3:-}}}}"
+  case "$prop" in
+    EnvironmentFiles) echo 'EnvironmentFiles={env_file} (ignore_errors=yes)' ;;
+    TimeoutStopUSec) echo 'TimeoutStopUSec=210000000' ;;
+    MainPID) echo 'MainPID=4242' ;;
+  esac
+  exit 0
+fi
+exit 1
+""",
+    )
+
+    result = _run_coordinator_verifier(tmp_path, env)
+
+    assert result.returncode != 0
+    assert "EnvironmentFile must be fail-closed, not optional" in result.stdout
+
+
+def test_coordinator_verifier_rejects_loose_truthy_allow_all_users(tmp_path: Path) -> None:
+    env_file, env = _coordinator_env(tmp_path)
+    env_file.write_text(
+        "TELEGRAM_BOT_TOKEN=123456789:ABCDEFGHIJKLMNOPQRSTUVWXYZ12\n"
+        "TELEGRAM_ALLOWED_USERS=12345,67890\n"
+        " GATEWAY_ALLOW_ALL_USERS = \"yes\" \n",
+        encoding="utf-8",
+    )
+    env_file.chmod(0o600)
+
+    result = _run_coordinator_verifier(tmp_path, env)
+
+    assert result.returncode != 0
+    assert "GATEWAY_ALLOW_ALL_USERS must be absent or explicitly false" in result.stdout
+    assert "12345" not in result.stdout
+    assert "67890" not in result.stdout
+
+
 def test_coordinator_verifier_requires_timeout_stop_210(tmp_path: Path) -> None:
     env_file, env = _coordinator_env(tmp_path)
     _write_fake_command(

```
