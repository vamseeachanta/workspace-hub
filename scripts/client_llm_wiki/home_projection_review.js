/* Explicit local Save/Load review pattern. No autosave, requests or app writes. */
(() => {
  'use strict';
  const fields = {
    section_id: document.getElementById('review-section'),
    comment: document.getElementById('review-comment'),
    decision: document.getElementById('review-decision'),
  };
  const message = document.getElementById('review-message');
  let dirty = false;
  const say = text => { message.textContent = text; };
  function validate(data) {
    const keys = ['schema', 'content_version', 'section_id', 'comment', 'decision'];
    if (!data || typeof data !== 'object' || Array.isArray(data) ||
        Object.keys(data).length !== keys.length || keys.some(k => !Object.hasOwn(data, k)) ||
        data.schema !== 1 || data.content_version !== reviewBinding.version ||
        !reviewBinding.sections.includes(data.section_id) ||
        typeof data.comment !== 'string' || data.comment.length > 4000 ||
        typeof data.decision !== 'string' || data.decision.length > 800 ||
        data.comment.includes('\0') || data.decision.includes('\0') ||
        !(data.comment.trim() || data.decision.trim())) {
      throw Error('Invalid, empty, stale or mismatched review JSON');
    }
    return data;
  }
  function collect() {
    return validate({schema: 1, content_version: reviewBinding.version,
      section_id: fields.section_id.value, comment: fields.comment.value,
      decision: fields.decision.value});
  }
  function parseSaved(text) {
    let body = text.trim();
    if (!body.startsWith('{') || !body.endsWith('}')) throw Error('Invalid review JSON');
    body = body.slice(1, -1);
    const result = Object.create(null);
    while (body.trim()) {
      const match = body.match(/^\s*("(?:\\.|[^"\\])*")\s*:\s*("(?:\\.|[^"\\])*"|(?:0|[1-9]\d*))\s*(,|$)/);
      if (!match) throw Error('Invalid flat review JSON');
      const key = JSON.parse(match[1]);
      if (Object.hasOwn(result, key)) throw Error('Duplicate review field');
      result[key] = JSON.parse(match[2]);
      body = body.slice(match[0].length);
      if (match[3] && !body.trim()) throw Error('Invalid trailing comma');
    }
    return validate(result);
  }
  document.getElementById('review-panel').addEventListener('input', () => {
    dirty = true; say('Unsaved review. Save review JSON to retain it.');
  });
  document.getElementById('review-save').onclick = () => {
    try {
      const data = collect();
      const blob = new Blob([JSON.stringify(data, null, 2)], {type: 'application/json'});
      if (blob.size > 16384) throw Error('Review file exceeds 16 KiB; shorten the entries');
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url; link.download = 'client-review-' + reviewBinding.version.slice(7, 19) + '.json';
      link.click(); setTimeout(() => URL.revokeObjectURL(url), 1000);
      say('Download requested. Confirm the file was saved. Your entries remain in this tab.');
    } catch (error) { say(error.message); }
  };
  document.getElementById('review-load').onchange = async event => {
    const file = event.target.files[0];
    if (!file) return;
    try {
      if (file.size > 16384) throw Error('Review file exceeds 16 KiB');
      const data = parseSaved(await file.text());
      if (dirty && !window.confirm('Replace the unsaved review in this tab? Save it first to keep it.')) {
        say('Load cancelled. Existing review preserved.'); return;
      }
      for (const key of ['section_id', 'comment', 'decision']) fields[key].value = data[key];
      dirty = false;
      say('Saved review loaded. Further edits require another Save review JSON.');
    } catch (error) { say('Load rejected: ' + error.message + '. Existing review preserved.'); }
    finally { event.target.value = ''; }
  };
  window.addEventListener('beforeunload', event => {
    if (dirty) { event.preventDefault(); event.returnValue = ''; }
  });
  window.clientHomeReview = {collect, validate, parseSaved};
})();
