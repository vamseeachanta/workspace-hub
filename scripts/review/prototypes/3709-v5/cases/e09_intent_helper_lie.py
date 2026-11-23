# ruff: noqa
"""E09 - the intent report is computed by uninspected helpers.

v3 predicate 7 only requires `absent` to be a comprehension whose iterator MENTIONS
`records`. Both the element expression and the membership test are delegated away.
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
    return []


def build_cutover_intent(records, new_lines, acknowledged=()):
    absent = [_absence(r) for r in _missing_occurrences(records, new_lines)]
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


def plan_cutover(current_text, classification_context, *, acknowledged=()):
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
