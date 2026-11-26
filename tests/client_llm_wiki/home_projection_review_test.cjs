const assert = require('node:assert/strict');

const controls = new Map();
function element(id) {
  if (!controls.has(id)) controls.set(id, new EventTarget());
  return controls.get(id);
}
global.document = {getElementById: element};
global.window = new EventTarget();
let prompts = 0;
window.confirm = () => { prompts++; return false; };
global.reviewBinding = {version: 'fixture', sections: ['weekly']};
require('../../scripts/client_llm_wiki/home_projection_review.js');

// EventTarget has no DOM tree. Deliver the bubbling event to the control
// and its enclosing panel, preserving the originating control.
function input(target) {
  const event = new Event('input', {bubbles: true});
  Object.defineProperty(event, 'target', {value: target});
  target.dispatchEvent(event);
  element('review-panel').dispatchEvent(event);
}

async function exerciseLoad() {
  const load = element('review-load');
  const comment = element('review-comment');
  const saved = JSON.stringify({schema: 1, content_version: 'fixture',
    section_id: 'weekly', comment: 'saved', decision: ''});
  load.files = [{size: saved.length, text: async () => saved}];
  input(load);
  await load.onchange({target: load});
  assert.equal(prompts, 0, 'a clean file selection must load without prompting');
  assert.equal(comment.value, 'saved');

  comment.value = 'local edit';
  input(comment);
  input(load);
  await load.onchange({target: load});
  assert.equal(prompts, 1, 'an unsaved edit must prompt before replacement');
  assert.equal(comment.value, 'local edit');
}
exerciseLoad().catch(error => { console.error(error); process.exitCode = 1; });
