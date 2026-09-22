// Logic and export checks only; these do not claim browser layout verification.
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {runInNewContext,Script} from 'node:vm';
const read=path=>readFileSync(new URL('../'+path,import.meta.url),'utf8');
const source=read('site/workshop/workshop.js');
const deck=read('docs/design-what-you-know/index.html');
const css=read('site/workshop/workshop.css');
const companion=read('site/workshop/prototype.html');
const slides=[...deck.matchAll(/<section class="slide[^>]*data-title="([^"]+)"/g)].map(m=>m[1]);
assert.equal(slides.length,13,'Thirteen slides');
assert.equal(slides[1],'What you’ll take away','Takeaways immediately after the opening');
assert.equal(slides[2],'Maps: whose route?','Maps follows takeaways');
const opening=deck.slice(deck.indexOf('<section class="slide ink hero"'),deck.indexOf('<section class="slide work takeaways-slide"'));
assert(opening.includes('images/join-talk.svg'),'QR on the opening slide');
assert(opening.includes('https://gchism94.github.io/talks/design-what-you-know/'),'Direct-link alternative to QR');
assert.equal(read('docs/assets/workshop/images/join-talk.svg'),read('site/workshop/images/join-talk.svg'),'QR exported unchanged');
function section(start,end){const a=source.indexOf(start),b=source.indexOf(end,a);assert(a>=0&&b>a);return source.slice(a,b);}
const configContext={window:{}};
runInNewContext(read('site/workshop/config.js'),configContext);
const defaults=configContext.window.WORKSHOP_DEFAULTS,config={...defaults};
const scriptURL=new URL('https://gchism94.github.io/talks/assets/workshop/workshop.js');
const provider=runInNewContext(section('  function providerURL(', '  function openURL(')+'\nproviderURL;',{
  URL,config,defaults,scriptURL,hostMatches:(h,d)=>h===d||h.endsWith('.'+d),
});
assert.equal(provider('figma'),'https://gchism94.github.io/talks/assets/workshop/prototype.html');
config.figma='https://www.figma.com/proto/example/workshop?node-id=1-2';
assert.equal(new URL(provider('figma')).hostname,'embed.figma.com');
config.figma='https://example.figma.site/';assert.equal(provider('figma'),config.figma);
for(const text of [source,css,deck])assert(text.includes('(max-width:900px), (max-height:540px)'),'Shared compact breakpoint');
assert(!/matchMedia\(['"]\(max-width:900px\)['"]\)/.test(source+deck),'No width-only navigation rule');
for(const visible of [false,true]){
  let focused='',paused=false;
  const prior={isConnected:true,getClientRects:()=>visible?[{}]:[],closest:()=>null,focus:()=>focused='prior'};
  const trigger={focus:()=>focused='trigger'};
  const device={dataset:{embed:'collective'},classList:{remove(){}},removeAttribute(){},querySelector:()=>trigger};
  const sibling={inert:true};
  runInNewContext(section('  function closeExpanded()',"  document.addEventListener('keydown'")+'\ncloseExpanded();',{
    expanded:device,restoreFocus:prior,inertState:[[sibling,false]],document:{body:{classList:{remove(){}}}},pauseDevice:()=>paused=true,
  });
  assert.equal(focused,visible?'prior':'trigger');assert(paused);assert.equal(sibling.inert,false);
}
// Exercise the exact companion script with lightweight controls, not a browser.
const next=[1,2,0,1].map(n=>({dataset:{next:String(n)}}));
const radios=[{value:'quiet',checked:false},{value:'close',checked:false}];
let focused=-1,scrolls=0;
const sections=[0,1,2].map(n=>({hidden:n!==0,querySelector:()=>({focus:()=>focused=n})}));
const elements={position:{textContent:''},outcome:{disabled:true},result:{textContent:''}},restart={};
const document={querySelectorAll:s=>s==='[data-step]'?sections:s==='[data-next]'?next:radios,querySelector:()=>restart,getElementById:id=>elements[id]};
const code=companion.match(/<script>([\s\S]*?)<\/script>/)[1];
runInNewContext(code,{document,window:{scrollTo:()=>scrolls++}});
next[0].onclick();assert.equal(focused,1);assert.equal(sections[1].hidden,false);
for(const [index,word] of [[0,'quieter'],[1,'shorter']]){
  radios[index].checked=true;radios[index].onchange();assert.equal(elements.outcome.disabled,false);assert(elements.result.textContent.includes(word));
  next[1].onclick();assert.equal(focused,2);assert.equal(sections[2].hidden,false);
  next[3].onclick();assert.equal(focused,1);assert.equal(radios[index].checked,true);
}
restart.onclick();assert.equal(focused,0);assert.equal(elements.outcome.disabled,true);assert(radios.every(r=>!r.checked));assert.equal(elements.result.textContent,'');assert(scrolls>0);
assert(!/fetch\(|localStorage|sessionStorage/.test(code),'Companion collects no responses');
for(const html of [deck,companion])for(const match of html.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/g))new Script(match[1]);
assert.equal(read('docs/assets/workshop/prototype.html'),companion,'Companion exported unchanged');
console.log('Mobile logic passed: shared breakpoints, default/custom prototypes, focus restoration, both starter choices, restart, no persistence, inline-script syntax. Browser checks still required.');
