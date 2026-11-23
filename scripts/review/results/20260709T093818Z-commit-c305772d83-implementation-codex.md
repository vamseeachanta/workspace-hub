### Verdict: MAJOR

### Summary
The implementation is broadly well covered and the added shell test suite passes locally, but I found a real quoting bug in the installer’s shell command generation. Because the installer persists commands into GNOME settings, path quoting needs to be correct for arbitrary checkout/home paths before this should land.

### Issues Found
- [P2] Important: scripts/agents/install-voice-dictation.sh:81 `shell_quote_word` does not round-trip values containing a single quote. For example, quoting `a'b` produces a shell word that evaluates to `a'\''b`, not `a'b`. This breaks persisted hotkey commands when `HOME`, `VOICE_DICTATION_INSTALL_ROOT`, `DICTATE_PYTHON`, or the checkout path contains an apostrophe. Replace this with a proven quoting primitive such as `printf '%q'` for bash commands, or fix the POSIX single-quote replacement to emit exactly `'foo'\''bar'`, and add a regression test that executes the stored gsettings command from a path containing `'`.

### Suggestions
- Add a static/runtime test for installer command generation with apostrophes and spaces in `HOME`, install root, and `DICTATE_PYTHON`.
- Consider running ShellCheck in CI for these scripts. It flagged the quote-adjacent `DICTATE_DEVICE_ALSA= "${BASH:-bash}" ...` form, which is valid but easy to misread.

### Questions for Author
- None.
