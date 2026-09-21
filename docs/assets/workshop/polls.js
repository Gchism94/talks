/* Native classroom spectrum. Shared D1 storage lives behind the existing gallery API. */
(() => {
  'use strict';
  const groups={maps:[['maps-google','Google Maps'],['maps-apple','Apple Maps']],music:[['music-spotify','Spotify'],['music-apple','Apple Music']]};
  const labels=['Mētis','Leans mētis','Both','Leans epistēmē','Epistēmē'];
  const widgets=[...document.querySelectorAll('[data-native-poll]')];
  let context=null, generation=0;
  function resolve(raw){
    const u=new URL(raw),local=['localhost','127.0.0.1'].includes(location.hostname);
    if(u.origin!=='https://techbytes-sketch-gallery.gchism.chatgpt.site'&&!(local&&u.origin==='http://localhost:4180'))throw Error('Open a configured classroom link.');
    let room=u.searchParams.get('room');
    if(document.body.hasAttribute('data-poll-page')&&new URL(location.href).searchParams.has('room'))room=new URL(location.href).searchParams.get('room');
    if(!/^[a-f0-9]{32}$/.test(room||''))throw Error('Ask your presenter for a classroom room link.');
    const key='techbytes-participant-'+room;
    let identity=localStorage.getItem(key);
    if(!/^[a-f0-9-]{36}$/.test(identity||'')){identity=crypto.randomUUID();localStorage.setItem(key,identity);}
    return {origin:u.origin,room,identity};
  }
  async function request(ctx,question,method='GET',score){
    const response=await fetch(ctx.origin+'/api/poll'+(method==='GET'?'?room='+ctx.room+'&question='+question:''),{
      method,credentials:'omit',cache:'no-store',signal:AbortSignal.timeout(12000),
      headers:{'X-Participant':ctx.identity,...(method==='POST'?{'Content-Type':'application/json'}:{})},
      ...(method==='POST'?{body:JSON.stringify({room:ctx.room,question,score,consent:true})}:{})
    });
    const data=await response.json();if(!response.ok)throw Error(data.error||'Could not connect. Try again.');return data;
  }
  const controllers=widgets.map((root,index)=>{
    const choices=groups[root.dataset.nativePoll];if(!choices)return null;
    let question=choices[0][0],states={},busy=false,sequence=0;
    root.classList.add('native-poll');
    root.innerHTML=`<div class="poll-topline"><span class="poll-eyebrow">Room pulse / not a scorecard</span><a class="poll-phone" target="_blank" rel="noopener">Vote on your phone ↗</a></div>
      <div class="poll-switch" role="group" aria-label="Choose an app">${choices.map(([id,name])=>`<button type="button" data-question="${id}" aria-pressed="${id===question}">${name}</button>`).join('')}</div>
      <fieldset class="poll-options"><legend>Whose knowledge shapes this interaction?</legend><div class="poll-scale">${labels.map((label,i)=>`<label><input type="radio" name="pulse-${index}" value="${i}"><span class="poll-dot" aria-hidden="true">${i+1}</span><span>${label}</span></label>`).join('')}</div></fieldset>
      <div class="poll-results" aria-label="Classroom response distribution" hidden></div>
      <div class="poll-bottom"><button class="poll-save" type="button" disabled>Save response</button><span class="poll-status" role="status" aria-live="polite">Connecting…</span></div>
      <p class="poll-disclosure">Saving shares a nameless response with this classroom. One editable response per browser, per app.</p>`;
    const status=root.querySelector('.poll-status'),save=root.querySelector('.poll-save'),results=root.querySelector('.poll-results');
    const inputs=[...root.querySelectorAll('input')];
    function state(){return states[question]||(states[question]={selected:null,data:null,error:''});}
    function render(){
      const s=state(),d=s.data;
      root.querySelectorAll('[data-question]').forEach(b=>{b.setAttribute('aria-pressed',String(b.dataset.question===question));b.disabled=busy;});
      inputs.forEach(input=>{input.checked=s.selected===Number(input.value);input.disabled=busy||!d||!d.open;});
      save.disabled=busy||!context||!d||!d.open||s.selected===null||s.selected===d.mine;
      save.textContent=busy?'Saving…':d?.mine!==null&&d?.mine!==undefined?'Update response':'Save response';
      status.textContent=s.error||(!d?'Connecting…':`${d.open?'Open':'Closed'} · ${d.total} responses · ${s.selected!==null&&s.selected!==d.mine?'Selection not saved':d.mine!==null?'Your response is saved':'Choose a position'}`);
      results.hidden=!d?.revealed;
      results.replaceChildren();
      if(d?.revealed&&Array.isArray(d.bins))d.bins.forEach((n,i)=>{
        const column=document.createElement('div'),bar=document.createElement('span'),count=document.createElement('b');
        column.setAttribute('aria-label',labels[i]+': '+n+' responses');bar.style.height=(56*n/Math.max(1,...d.bins))+'px';count.textContent=String(n);column.append(count,bar);results.append(column);
      });
      root.querySelector('.poll-phone').href='https://gchism94.github.io/talks/polls/'+(context?'?room='+context.room:'');
    }
    async function refresh(){
      if(!context||busy)return;
      const ctx=context,epoch=generation,q=question,seq=++sequence;
      try{const d=await request(ctx,q);if(epoch!==generation||q!==question||seq!==sequence)return;const s=state();s.data=d;s.error='';if(s.selected===null&&d.mine!==null)s.selected=d.mine;render();}
      catch{if(epoch!==generation||q!==question||seq!==sequence)return;state().error='Connection unavailable. Selection not submitted; discuss aloud or retry.';render();}
    }
    root.querySelectorAll('[data-question]').forEach(b=>b.addEventListener('click',()=>{question=b.dataset.question;sequence++;render();refresh();}));
    inputs.forEach(input=>input.addEventListener('change',()=>{state().selected=Number(input.value);render();}));
    save.addEventListener('click',async()=>{
      if(save.disabled||!context)return;
      const ctx=context,epoch=generation,q=question,s=state(),score=s.selected;busy=true;sequence++;s.error='';render();
      try{await request(ctx,q,'POST',score);if(epoch!==generation)return;s.data.mine=score;s.error='Saved to classroom storage.';}
      catch(e){if(epoch===generation)s.error='Not confirmed saved. '+e.message+' Retry is safe.';}
      finally{if(epoch===generation){busy=false;render();}}
      if(epoch===generation&&s.data.mine===score)refresh();
    });
    // Retry without requiring a reload (including a failed initial connection).
    const retry=document.createElement('button');retry.type='button';retry.className='poll-retry';retry.textContent='Refresh';retry.addEventListener('click',refresh);root.querySelector('.poll-bottom').append(retry);
    return {refresh,reset(error=''){states={};busy=false;sequence++;if(error)state().error=error;render();if(!error)refresh();},visible(){return root.getBoundingClientRect().width>0&&(!root.closest('.slide')||root.closest('.slide').classList.contains('active'));}};
  }).filter(Boolean);
  function configure(raw){generation++;try{context=resolve(raw);controllers.forEach(c=>c.reset());}catch{context=null;controllers.forEach(c=>c.reset('Open a classroom link and allow browser storage to save responses.'));}}
  document.addEventListener('workshop:links',e=>configure(e.detail.gallery));
  configure(window.TECHBYTES_GALLERY||window.WORKSHOP_DEFAULTS?.gallery||'');
  setInterval(()=>{if(!document.hidden)controllers.forEach(c=>{if(c.visible())c.refresh();});},10000);
  document.addEventListener('visibilitychange',()=>{if(!document.hidden)controllers.forEach(c=>{if(c.visible())c.refresh();});});
})();
