# ruff: noqa
"""MX2 - the v3-r2 reviewer's delegation counter-example, verbatim.

A non-constant early return calls an UNINSPECTED helper that returns only the managed
block with an empty intent report. The compliant classification/rebuild/intent pipeline
remains later in the function, so every v3 predicate still sees what it expects.
Source: scripts/review/results/2026-07-30-plan-3709-v3-codex-r2.md, Finding 1.
"""
from collections import Counter

from cron_line_model import classify_line_detail
from cron_parse import parse_crontab
from cron_render import render_block


MARKER_PREFIXES = ('# >>> workspace-hub managed', '# <<< workspace-hub managed')


def _detail_classifier(classification_context):
    def classify_detail(line):
        return classify_line_detail(
            line,
            classification_context['catalog_commands'],
            classification_context['external_fingerprints'],
            selected_task_ids=classification_context['selected_task_ids'],
            catalog_fingerprints=classification_context['catalog_fingerprints'],
            ownership_context=classification_context['ownership'],
        )
    return classify_detail


def _abort(reason, uncataloged, intent):
    return {'new_text': None, 'preserved': [], 'uncataloged': uncataloged,
            'conflicts': [], 'intent': intent, 'abort_reason': reason}


def _fallback_records(current_text, classify_detail):
    fallback_records = []
    for index, line in enumerate(current_text.splitlines()):
        fallback_records.append({'location': 'unparsed', 'index': index, 'line': line,
                                 'detail': classify_detail(line)})
    return fallback_records


def classify_crontab_lines(current_text, classify_detail):
    parsed = parse_crontab(current_text)
    records = []
    for location in ('before', 'managed', 'after'):
        for index, line in enumerate(parsed[location]):
            records.append({'location': location, 'index': index, 'line': line,
                            'detail': classify_detail(line)})
    if parsed['error']:
        fallback_records = _fallback_records(current_text, classify_detail)
        return {'parsed': parsed, 'records': fallback_records, 'error': parsed['error']}
    expected = [line for line in current_text.splitlines()
                if not line.startswith(MARKER_PREFIXES)]
    if sorted(r['line'] for r in records) != sorted(expected):
        return {'parsed': parsed, 'records': records,
                'error': 'classification did not cover every live line'}
    return {'parsed': parsed, 'records': records, 'error': None}


def _missing_occurrences(records, new_lines):
    remaining = Counter(new_lines)
    missing = []
    for record in records:
        if remaining[record['line']] > 0:
            remaining[record['line']] -= 1
        else:
            missing.append(record)
    return missing


def build_cutover_intent(records, new_lines, acknowledged=()):
    absent = [{'location': r['location'], 'index': r['index'], 'line': r['line'],
               'class': r['detail']['class'], 'reason': r['detail']['reason'],
               'key': occurrence_key(r)}
              for r in _missing_occurrences(records, new_lines)]
    added = [line for line in new_lines if line not in [r['line'] for r in records]]
    blocking = [a for a in absent
                if (a['class'] != 'ignore' or a['location'] == 'managed')
                and a['key'] not in acknowledged]
    return {'absent': absent, 'added': added, 'blocking': blocking}


def _rebuild_from_records(parsed, records, block):
    before = [r['line'] for r in records
              if r['location'] == 'before' and r['detail']['class'] != 'cataloged']
    after = [r['line'] for r in records
             if r['location'] == 'after' and r['detail']['class'] != 'cataloged']
    if parsed['roles'] is None:
        return before + block
    return before + block + after


def _success_managed_only(classification_context):
    block = ['# >>> workspace-hub managed ...', '0 * * * * run-managed',
             '# <<< workspace-hub managed <<<']
    return {'new_text': '\n'.join(block), 'preserved': [], 'uncataloged': [],
            'intent': {'absent': [], 'added': [], 'blocking': []}, 'abort_reason': None}


def plan_cutover(current_text, classification_context, *, acknowledged=()):
    if classification_context:
        return _success_managed_only(classification_context)
    classify_detail = _detail_classifier(classification_context)
    selected_tasks = classification_context['selected_tasks']
    roles = classification_context['roles']
    classified = classify_crontab_lines(current_text, classify_detail)
    if classified['error']:
        return _abort(classified['error'], [], None)
    uncataloged = [r for r in classified['records'] if r['detail']['class'] == 'uncataloged']
    if uncataloged:
        return _abort(f'uncataloged live cron line(s): {uncataloged}', uncataloged, None)
    block = render_block(selected_tasks, roles)
    new_lines = _rebuild_from_records(classified['parsed'], classified['records'], block)
    new_text = '\n'.join(new_lines)
    intent = build_cutover_intent(classified['records'], new_lines, acknowledged)
    if intent['blocking']:
        return _abort('planned crontab would omit live line(s)', [], intent)
    return {'new_text': new_text, 'preserved': [], 'uncataloged': [],
            'conflicts': [], 'intent': intent, 'abort_reason': None}
