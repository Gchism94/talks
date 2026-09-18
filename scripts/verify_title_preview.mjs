// Test the production preview policy without loading the external simulation.
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { runInNewContext } from 'node:vm';

const source = readFileSync(new URL('../site/workshop/workshop.js', import.meta.url), 'utf8');
function section(start, end) {
  const a = source.indexOf(start), b = source.indexOf(end, a);
  assert.ok(a >= 0 && b > a, `Locate ${start}`);
  return source.slice(a, b);
}
const defaults = { collective: 'https://collective-movement.vercel.app/' };
const config = { ...defaults };
const providerURL = runInNewContext(`${section('  function providerURL(', '  function openURL(')}\nproviderURL;`, { URL, defaults, config });
for (const [kind, full, embed, experience] of [
  ['birds', false, 'title', 'original'],
  ['birds', true, '1', 'original'],
  ['practice', false, '1', 'practice'],
  ['collective', false, '1', null],
]) {
  const url = new URL(providerURL(kind, full));
  assert.equal(url.origin, 'https://collective-movement.vercel.app');
  assert.equal(url.searchParams.get('embed'), embed);
  assert.equal(url.searchParams.get('experience'), experience);
}
config.collective += '?experience=practice&embed=1';
assert.equal(new URL(providerURL('birds')).searchParams.get('experience'), 'original');

const document = { hidden: false }, reducedMotion = { matches: false };
const calls = [];
let active = true, hiddenRoute = false;
const device = {
  dataset: { embed: 'birds' },
  closest: selector => selector === '.slide.active' ? (active ? {} : null) : (hiddenRoute ? {} : null),
};
const { shouldPlayPreview, updateActive } = runInNewContext(
  `${section('  function shouldPlayPreview(', "  document.addEventListener('deck:change'")}\n({shouldPlayPreview, updateActive});`,
  { document, reducedMotion, devices: [device], loadDevice: d => calls.push(['load', d]), pauseDevice: d => calls.push(['pause', d]) },
);
let policies = 0;
for (let mask = 0; mask < 64; mask++) {
  document.hidden = !!(mask & 1);
  active = !!(mask & 2);
  hiddenRoute = !!(mask & 4);
  device.dataset.previewPaused = mask & 8 ? 'true' : 'false';
  reducedMotion.matches = !!(mask & 16);
  device.dataset.previewRequested = mask & 32 ? 'true' : 'false';
  const expected = !document.hidden && active && !hiddenRoute && !(mask & 8) && (!reducedMotion.matches || !!(mask & 32));
  assert.equal(shouldPlayPreview(device), expected, `Autoplay policy ${mask}`);
  calls.length = 0;
  updateActive();
  assert.equal(calls[0][0], expected ? 'load' : 'pause');
  policies++;
}

const pauseDevice = runInNewContext(`${section('  function pauseDevice(', '  function expand(')}\npauseDevice;`, { URL, refreshPreviewControl: () => {} });
for (const kind of ['birds', 'collective', 'practice', 'spotify']) {
  const messages = [], cover = { hidden: true };
  let removed = false;
  const frame = {
    src: defaults.collective,
    contentWindow: { postMessage: (message, origin) => messages.push([message.type, origin]) },
    remove: () => { removed = true; },
  };
  pauseDevice({ dataset: { embed: kind }, querySelector: s => s === 'iframe' ? frame : cover });
  assert.equal(removed, ['birds', 'spotify'].includes(kind));
  assert.equal(cover.hidden, !removed);
  if (kind !== 'spotify') assert.deepEqual(messages, [['collective:pause', 'https://collective-movement.vercel.app']]);
}
pauseDevice({ querySelector: () => null });
console.log(`Title preview: URL modes, ${policies} autoplay policies, and pause/unload behavior passed.`);
