// Exercise the actual browser adapter validator without contacting a poll provider.
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { runInNewContext } from 'node:vm';

const source = readFileSync(new URL('../site/workshop/workshop.js', import.meta.url), 'utf8');
const start = source.indexOf('  function validate(key, value) {');
const end = source.indexOf('  function validConfig(raw) {', start);
assert.ok(start >= 0 && end > start, 'Locate the production URL validator');
const validate = runInNewContext(`${source.slice(start, end)}\nvalidate;`, {
  URL,
  localHost: false,
  hostMatches: (host, domain) => host === domain || host.endsWith('.' + domain),
});

let checks = 0;
for (const key of ['mapsPoll', 'spotifyPoll']) {
  const responseLink = 'https://pe.app/response_links/00000000-0000-4000-8000-000000000001/start';
  assert.equal(validate(key, responseLink), responseLink);
  checks++;
  for (const url of [
    'https://pe.app/a/my_polls',
    'https://pe.app/a/shares/123?tab=Presenters',
    'https://pe.app/gregchism',
    responseLink.replace('pe.app', 'pe.app.example.org'),
    responseLink.replace('pe.app', 'pe.app:444'),
    responseLink.replace('/start', '/edit'),
    responseLink + '?private=1',
    responseLink + '#participant=private',
  ]) {
    assert.throws(() => validate(key, url), 'Only the official pe.app participant response-link shape is allowed');
    checks++;
  }
  for (const host of ['pollev-embeds.com', 'embed.polleverywhere.com', 'pollev.com']) {
    const url = `https://${host}/techbytes-adapter-test`;
    assert.equal(validate(key, url), url);
    checks++;
  }
  assert.equal(validate(key, ''), '');
  checks++;
  for (const url of [
    'http://pollev-embeds.com/techbytes-adapter-test',
    'https://pollev-embeds.com.example.org/techbytes-adapter-test',
    'https://notpollev-embeds.com/techbytes-adapter-test',
    'https://presenter:password@pollev-embeds.com/techbytes-adapter-test',
    'https://pollev-embeds.com/admin/example',
    'https://pollev-embeds.com/example?token=private',
    'https://example.org/techbytes-adapter-test',
  ]) {
    assert.throws(() => validate(key, url), `${key} should reject ${url}`);
    checks++;
  }
}
const config = readFileSync(new URL('../site/workshop/config.js', import.meta.url), 'utf8');
assert.equal(validate('gallery','https://techbytes-sketch-gallery.gchism.chatgpt.site/?room='+'a'.repeat(32)), 'https://techbytes-sketch-gallery.gchism.chatgpt.site/?room='+'a'.repeat(32));
for (const url of ['https://example.org/?room='+'a'.repeat(32), 'https://techbytes-sketch-gallery.gchism.chatgpt.site/?room=wrong', 'https://techbytes-sketch-gallery.gchism.chatgpt.site/?room='+'a'.repeat(32)+'#participant=private']) assert.throws(()=>validate('gallery',url));
const context = { window: {} };
runInNewContext(config, context);
for (const key of ['mapsPoll', 'spotifyPoll']) {
  const value = context.window.WORKSHOP_DEFAULTS[key];
  assert.equal(value.includes('techbytes-adapter-test'), false, 'Never publish adapter fixtures');
  validate(key, value);
}
validate('gallery', context.window.WORKSHOP_DEFAULTS.gallery);
console.log(`${checks} URL checks passed; public defaults contain no test fixtures.`);
