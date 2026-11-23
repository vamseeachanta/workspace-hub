"""v3's textual mutation battery, applied to the v4 reference.

v3 published fifteen named mutations plus its counter-example and claimed all
sixteen were rejected; the prototype that produced that claim was not committed.
These are re-expressed against the v4 reference so the carry-forward is measured.

M8, M9 and M10 are shape mutations rather than single-token edits; they are
embodied verbatim in `cases/mx1_v3_counterexample.py`, which is a rejection case
in its own right.

Each entry is (id, description, find, replace). Applying it must flip the
attestation to False.
"""
from __future__ import annotations

from pathlib import Path

REFERENCE = (Path(__file__).resolve().parent / "cases" / "reference.py").read_text()

NAMED_MUTATIONS = (
    ("M1", "classify only two of the three locations",
     "for location in ('before', 'managed', 'after'):",
     "for location in ('before', 'after'):"),
    ("M2", "delete the uncataloged abort guard",
     "    if uncataloged:\n"
     "        return _abort(f'uncataloged live cron line(s): {uncataloged}', uncataloged, None)\n",
     ""),
    ("M3", "hoist render_block above the classification",
     "    classified = classify_crontab_lines(current_text, classify_detail)",
     "    block = render_block(selected_tasks, roles)\n"
     "    classified = classify_crontab_lines(current_text, classify_detail)"),
    ("M3b", "add an unused render_block decoy above the classification",
     "    classified = classify_crontab_lines(current_text, classify_detail)",
     "    block0 = render_block(selected_tasks, roles)\n"
     "    classified = classify_crontab_lines(current_text, classify_detail)"),
    ("M4", "empty the `before` retention comprehension",
     "    before = [r['line'] for r in records\n"
     "              if r['location'] == 'before' and r['detail']['class'] != 'cataloged']",
     "    before = []"),
    ("M5", "drop `after` from the rebuilt result",
     "    return before + block + after", "    return before + block"),
    ("M6", "delete the blocking-intent abort guard",
     "    if intent['blocking']:\n"
     "        return _abort('planned crontab would omit live line(s)', [], intent)\n", ""),
    ("M7", "delete the parse-error abort guard",
     "    if classified['error']:\n"
     "        return _abort(classified['error'], [], None)\n", ""),
    ("M11", "`_fallback_records` returns an empty list",
     "    fallback_records = []\n"
     "    for index, line in enumerate(current_text.splitlines()):\n"
     "        fallback_records.append({'location': 'unparsed', 'index': index, 'line': line,\n"
     "                                 'detail': classify_detail(line)})\n"
     "    return fallback_records",
     "    return []"),
    ("M12", "the success return emits the block instead of new_text",
     "    return {'new_text': new_text, 'preserved': [], 'uncataloged': [],",
     "    return {'new_text': '\\n'.join(block), 'preserved': [], 'uncataloged': [],"),
    ("M13", "make the record append conditional inside the inner loop",
     "            records.append({'location': location, 'index': index, 'line': line,\n"
     "                            'detail': classify_detail(line)})",
     "            if line.strip():\n"
     "                records.append({'location': location, 'index': index, 'line': line,\n"
     "                                'detail': classify_detail(line)})"),
    ("M14", "pass an empty record list to the rebuild",
     "_rebuild_from_records(classified['parsed'], classified['records'], block)",
     "_rebuild_from_records(classified['parsed'], [], block)"),
)


def apply(mutation):
    _id, _why, find, replace = mutation
    if find not in REFERENCE:
        raise AssertionError(f"{_id}: anchor not found in the reference")
    return REFERENCE.replace(find, replace, 1)
