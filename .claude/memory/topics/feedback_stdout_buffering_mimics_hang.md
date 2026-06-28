> Git-tracked snapshot from Claude auto-memory. Captured: 2026-06-26
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_stdout_buffering_mimics_hang.md

---
name: feedback-stdout-buffering-mimics-hang
description: "Empty log from a `>`-redirected script killed by timeout looks like a hang but is usually buffered stdout; probe unbuffered + faulthandler before claiming hung"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 21a4805d-3780-4e54-b2ed-9cf1350decb2
---

A script run as `cmd > log 2>&1` (or piped to `tail`) that a `timeout`/SIGKILL terminates with an
**empty log** is NOT evidence of a hang. Python (and most tools) **block-buffer stdout when it is
not a TTY**, so the buffered output is discarded on SIGKILL and the log looks empty even though the
process was printing/working normally.

**Why:** On 2026-05-28 (Doris demo, #2859) I ran `digitalmodel/examples/demos/gtm/demo_01...` as
`> /tmp/log; timeout 80` → empty log + exit 124, and wrongly concluded "the GTM demo harness hangs
locally." It does not — it completes in ~1.8–2.4s and writes a branded HTML report. The empty log
was pure buffering (compounded by CPU contention from a stray pytest I hadn't fully killed, and a
wrong `PYTHONPATH` missing the script's own dir). I committed the false "hangs" claim into a
capability matrix and an issue comment, then had to self-correct. All 5 gtm demos actually run exit 0.

**How to apply:** before ever calling a script hung/slow when its redirected log is empty —
1. Re-run **unbuffered**: `PYTHONUNBUFFERED=1` or `python -u` (output appears immediately).
2. Get a stack dump at the suspected hang point: `python -u -c "import faulthandler,runpy; faulthandler.dump_traceback_later(35, exit=True); runpy.run_path('<script>', run_name='__main__')"` — the traceback prints the exact file:line if it really is stuck; if it never fires, the script finished first.
3. Check `python -X importtime` — heavy imports (plotly/pandas/IPython chain) can be ~1.5s and look like a stall.
4. Run in isolation (no competing CPU load) and with the script's documented `PYTHONPATH`/flags (READMEs often want the script's own dir on the path, e.g. `examples/demos/gtm:src`).

Reinforces the SOUL.md gate "Verify before claiming success" and "correct when wrong." Related: [[feedback_codex_sandbox_uv_cache_readonly]] (uv-run alternative), [[project_doris_demo]].
