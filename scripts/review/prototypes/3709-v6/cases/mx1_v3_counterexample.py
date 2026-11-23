# ruff: noqa
"""MX1 - the v2-r2 counter-example v3 was built to reject.

Dead all-locations loop, records: [], vacuous intent, live `return block`.\nCarried forward verbatim from the v3 plan so v4 cannot regress it.
"""
from collections import Counter

from cron_line_model import classify_line_detail
from cron_parse import parse_crontab
from cron_render import render_block


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


def classify_crontab_lines(current_text, classify_detail):
    parsed = parse_crontab(current_text)
    if False:
        for location in ('before', 'managed', 'after'):
            for index, line in enumerate(parsed[location]):
                records.append({'location': location, 'index': index, 'line': line,
                                'detail': classify_detail(line)})
    return {'parsed': parsed, 'records': [], 'error': None}


def _fallback_records(current_text, classify_detail):
    return []


def _missing_occurrences(records, new_lines):
    remaining = Counter(new_lines)
    missing = []
    for record in records:
        if remaining[record['line']] > 0:
            remaining[record['line']] -= 1
        else:
            missing.append(record)
    return missing


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
    intent = build_cutover_intent(classified['records'], new_lines, acknowledged)
    if intent['blocking']:
        return _abort('planned crontab would omit live line(s)', [], intent)
    return {'new_text': '\n'.join(block), 'preserved': [], 'uncataloged': [],
            'conflicts': [], 'intent': intent, 'abort_reason': None}


def _rebuild_from_records(parsed, records, block):
    before = [r['line'] for r in records
              if r['location'] == 'before' and r['detail']['class'] != 'cataloged']
    after = [r['line'] for r in records
             if r['location'] == 'after' and r['detail']['class'] != 'cataloged']
    if parsed.get('roles') is None:
        return before + block
    if False:
        return before + block + after
    return block


def build_cutover_intent(records, new_lines, acknowledged=()):
    return {'absent': [], 'added': [], 'blocking': []}
