import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { runInNewContext } from 'node:vm';
const source=readFileSync(new URL('../site/workshop/sketch.js',import.meta.url),'utf8');
const start=source.indexOf('  const blank='),end=source.indexOf("  for(const studio of document.querySelectorAll",start);
assert.ok(start>=0&&end>start,'Locate the real draft schema');
const {blank,validDraft}=runInNewContext(source.slice(start,end)+'\n({blank,validDraft});');
const example={...blank(),title:'A learner can explain',description:'Keep uncertainty visible.',notice:'The next action',knowledge:'Room for their experience',person:'A first-time contributor',task:'Describe the recording',strokes:[[[.1,.2],[.3,.4]],[[0,1]]]};
assert.equal(JSON.stringify(validDraft(JSON.parse(JSON.stringify(example)))),JSON.stringify(example),'Saved coordinates and every answer survive JSON recovery');
assert.equal(JSON.stringify(validDraft(blank())),JSON.stringify(blank()),'An unfinished blank draft can recover');
for(const value of [null,{}, {...example,strokes:[[[Infinity,0]]]}, {...example,strokes:[[[2,0]]]}, {...example,strokes:[[]]}, {...example,title:'x'.repeat(101)}, {...example,description:'x'.repeat(1501)}, {...example,strokes:Array(301).fill([[.2,.3]])}, {...example,strokes:[Array(6001).fill([.2,.3])]}]) {
  assert.throws(()=>validDraft(value),'Reject malformed/oversized recovery data');
}
console.log('Sketch draft recovery schema: JSON round trip, all answers, normalized points, empty drafts, malformed and oversized data passed.');
