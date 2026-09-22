/* Device-local recovery plus explicit, retry-safe classroom submissions. */
(() => {
  'use strict';
  const BASE_KEY='techbytes-sketch-v2';
  const briefInputs=[...document.querySelectorAll('.brief-board input')];
  const blank=()=>({title:'',description:'',notice:'',knowledge:'',person:'',task:'',strokes:[]});
  function validDraft(raw) {
    const d=blank();
    if(!raw||typeof raw!=='object')throw Error('Invalid draft');
    for(const [key,max] of Object.entries({title:100,description:1500,notice:600,knowledge:600,person:120,task:160})){
      if(typeof raw[key]!=='string'||raw[key].length>max)throw Error('Invalid answer');
      d[key]=raw[key];
    }
    let count=0;
    if(!Array.isArray(raw.strokes)||raw.strokes.length>300)throw Error('Invalid sketch');
    d.strokes=raw.strokes.map(line=>{
      if(!Array.isArray(line)||!line.length||(count+=line.length)>6000)throw Error('Invalid stroke');
      return line.map(p=>{if(!Array.isArray(p)||p.length!==2||!p.every(n=>Number.isFinite(n)&&n>=0&&n<=1))throw Error('Invalid point');return [...p];});
    });
    return d;
  }
  for(const studio of document.querySelectorAll('[data-sketch]')){
    const canvas=studio.querySelector('canvas'),ctx=canvas.getContext('2d'),description=studio.querySelector('textarea');
    let draft=blank(),stroke=null,busy=false,identity='',room='',endpoint='',lastKey=BASE_KEY;
    const compact=matchMedia('(max-width:900px), (max-height:540px)');
    let drawing=!compact.matches,pointerId=null,strokeBox=null,pointCount=0,paintedPoints=0,paintFrame=0,fullPaint=false;
    const toolbar=studio.querySelector('.sketch-toolbar'),drawToggle=document.createElement('button');
    drawToggle.type='button';drawToggle.className='sketch-draw-toggle';
    toolbar.insertBefore(drawToggle,toolbar.querySelector('button'));
    function updateDrawingMode(){
      studio.classList.toggle('is-drawing',drawing);
      drawToggle.textContent=drawing?'Done drawing':'Draw';
      drawToggle.setAttribute('aria-pressed',String(drawing));
      canvas.setAttribute('aria-label',drawing?'Drawing mode. Select Done drawing to scroll over this area.':'Sketch preview. Scroll normally, or select Draw to add strokes. Text answers are also available.');
    }
    drawToggle.onclick=()=>{finishStroke();drawing=!drawing;updateDrawingMode();};
    updateDrawingMode();
    studio.querySelector('label[for=sketchDescription]').textContent='The idea, and why it might help';
    const titleLabel=document.createElement('label');titleLabel.htmlFor='sketchTitle';titleLabel.textContent='A short title';
    const title=document.createElement('input');title.id='sketchTitle';title.maxLength=100;title.placeholder='Name the idea, not the group';
    studio.insertBefore(titleLabel,studio.firstChild);titleLabel.after(title);
    const details=document.createElement('details');details.className='sketch-reasoning';
    details.innerHTML='<summary>Answer the two design questions</summary><label for="sketchNotice">What should someone notice first?</label><textarea id="sketchNotice" maxlength="600"></textarea><label for="sketchKnowledge">Where can their knowledge change the outcome?</label><textarea id="sketchKnowledge" maxlength="600"></textarea>';
    description.after(details);
    const actions=document.createElement('div');actions.className='sketch-actions';
    actions.innerHTML='<label class="sketch-consent"><input type="checkbox"> Share this sketch and answers with the classroom. No names or private information.</label><div><button type="button" class="interaction-button primary" data-submit-sketch>Submit idea</button><button type="button" class="interaction-button" data-download-sketch>Download draft</button><a class="interaction-button" data-gallery-link target="_blank" rel="noopener noreferrer">Gallery & vote ↗</a></div><p data-sketch-status role="status"></p>';
    studio.append(actions);
    const notice=details.querySelector('#sketchNotice'),knowledge=details.querySelector('#sketchKnowledge'),consent=actions.querySelector('input'),submit=actions.querySelector('[data-submit-sketch]'),galleryLink=actions.querySelector('[data-gallery-link]'),status=actions.querySelector('[role=status]'),caption=studio.querySelector('.embed-caption');
    function snapshot(){draft={...draft,title:title.value,description:description.value,notice:notice.value,knowledge:knowledge.value,person:briefInputs[0]?.value||'',task:briefInputs[1]?.value||''};return draft;}
    function persist(){
      try{localStorage.setItem(lastKey,JSON.stringify(snapshot()));caption.textContent='Draft saved on this device. Submit to share it with the room.';return true;}
      catch{caption.textContent='Device storage failed. Download your draft before leaving.';return false;}
    }
    function render(){
      const r=canvas.getBoundingClientRect();if(!r.width)return;
      const dpr=Math.min(devicePixelRatio||1,2),width=Math.round(r.width*dpr),height=Math.round(r.height*dpr);
      // Only resize the backing bitmap when its size changes, never on every move.
      if(canvas.width!==width)canvas.width=width;if(canvas.height!==height)canvas.height=height;
      ctx.setTransform(dpr,0,0,dpr,0,0);ctx.clearRect(0,0,r.width,r.height);ctx.strokeStyle='#ab3e2b';ctx.fillStyle='#ab3e2b';ctx.lineWidth=2.5;ctx.lineCap='round';ctx.lineJoin='round';
      for(const line of draft.strokes){ctx.beginPath();if(line.length===1){ctx.arc(line[0][0]*r.width,line[0][1]*r.height,1.5,0,Math.PI*2);ctx.fill();}else{line.forEach((p,i)=>ctx[i?'lineTo':'moveTo'](p[0]*r.width,p[1]*r.height));ctx.stroke();}}
      paintedPoints=stroke?.length||0;
    }
    function schedulePaint(full=false){
      fullPaint=fullPaint||full;if(paintFrame)return;
      paintFrame=requestAnimationFrame(()=>{
        paintFrame=0;
        if(fullPaint){fullPaint=false;render();return;}
        if(!stroke||!strokeBox||paintedPoints===stroke.length)return;
        const {width,height}=strokeBox;ctx.beginPath();
        if(stroke.length===1){ctx.arc(stroke[0][0]*width,stroke[0][1]*height,1.5,0,Math.PI*2);ctx.fill();}
        else {const start=Math.max(0,paintedPoints-1);ctx.moveTo(stroke[start][0]*width,stroke[start][1]*height);for(let i=start+1;i<stroke.length;i++)ctx.lineTo(stroke[i][0]*width,stroke[i][1]*height);ctx.stroke();}
        paintedPoints=stroke.length;
      });
    }
    function finishStroke(){
      if(pointerId===null)return;
      const id=pointerId;pointerId=null;stroke=null;strokeBox=null;
      if(canvas.hasPointerCapture(id))canvas.releasePointerCapture(id);
      schedulePaint(true);persist();
    }
    function hydrate(){title.value=draft.title;description.value=draft.description;notice.value=draft.notice;knowledge.value=draft.knowledge;briefInputs.forEach((el,i)=>el.value=draft[i?'task':'person']);pointCount=draft.strokes.reduce((n,line)=>n+line.length,0);schedulePaint(true);}
    function connect(value){
      const previous=room;endpoint='';room='';identity='';
      try{if(value){const u=new URL(value);if(u.hostname==='techbytes-sketch-gallery.gchism.chatgpt.site'&&u.protocol==='https:'){endpoint=u.origin;room=u.searchParams.get('room')||'';}}}catch{}
      if(previous!==room)consent.checked=false;
      lastKey=BASE_KEY+(room?':'+room:'');
      let saved;
      try {
        const raw=localStorage.getItem(lastKey);
        if(raw)saved=validDraft(JSON.parse(raw));
        // Carry an unsubmitted draft into the first connected classroom, without discarding it.
        else if(room&&!previous){const loose=localStorage.getItem(BASE_KEY);if(loose)saved=validDraft(JSON.parse(loose));}
        if(saved){draft=saved;hydrate();}
        if(room){const key='techbytes-participant-'+room;identity=localStorage.getItem(key)||crypto.randomUUID();localStorage.setItem(key,identity);}
      }catch{status.textContent='A saved draft or browser identity could not be restored. Download your current work before reloading.';}
      submit.disabled=!room||!identity;submit.textContent=room?'Submit idea':'Connect a classroom';
      galleryLink.hidden=!endpoint;
      if(endpoint)galleryLink.href=endpoint+'/?room='+room+(identity?'#participant='+identity:'');
      if(!room)status.textContent='No classroom connected. Drafts and downloads still work; the presenter can add a room under Links.';
    }
    [title,description,notice,knowledge,...briefInputs].forEach(el=>el.addEventListener('input',persist));
    const point=e=>{const r=strokeBox;return [Math.max(0,Math.min(1,+((e.clientX-r.left)/r.width).toFixed(4))),Math.max(0,Math.min(1,+((e.clientY-r.top)/r.height).toFixed(4)))];};
    canvas.onpointerdown=e=>{
      if(!drawing||e.button!==0||!e.isPrimary||pointerId!==null)return;
      if(draft.strokes.length>=300||pointCount>=6000){status.textContent='Sketch limit reached. Use Undo or describe the idea.';return;}
      render();strokeBox=canvas.getBoundingClientRect();pointerId=e.pointerId;stroke=[point(e)];draft.strokes.push(stroke);pointCount++;paintedPoints=0;canvas.setPointerCapture(pointerId);schedulePaint();
    };
    canvas.onpointermove=e=>{
      if(!stroke||e.pointerId!==pointerId)return;
      if(pointCount>=6000){finishStroke();status.textContent='Sketch limit reached. Use Undo or describe the idea.';return;}
      const p=point(e),last=stroke[stroke.length-1];if(p[0]===last[0]&&p[1]===last[1])return;
      stroke.push(p);pointCount++;schedulePaint();
    };
    canvas.onpointerup=canvas.onpointercancel=canvas.onlostpointercapture=e=>{if(e.pointerId===pointerId)finishStroke();};
    studio.querySelector('[data-undo-sketch]').onclick=()=>{finishStroke();pointCount-=draft.strokes.pop()?.length||0;schedulePaint(true);persist();};
    studio.querySelector('[data-clear-sketch]').onclick=()=>{finishStroke();if(!draft.strokes.length||!confirm('Clear the drawing on this device? Submitted work will not change until you submit again.'))return;draft.strokes=[];pointCount=0;schedulePaint(true);persist();};
    new ResizeObserver(()=>schedulePaint(true)).observe(canvas);
    const leaveDrawing=()=>{finishStroke();if(compact.matches){drawing=false;updateDrawingMode();}};
    compact.addEventListener('change',()=>{finishStroke();drawing=!compact.matches;updateDrawingMode();});
    document.addEventListener('deck:change',leaveDrawing);
    window.addEventListener('blur',leaveDrawing);
    document.addEventListener('visibilitychange',()=>{if(document.hidden){leaveDrawing();persist();}});
    actions.querySelector('[data-download-sketch]').onclick=()=>{
      const url=URL.createObjectURL(new Blob([JSON.stringify({format:'techbytes-sketch-v1',...snapshot()},null,2)],{type:'application/json'}));
      const a=document.createElement('a');a.href=url;a.download='my-techbytes-sketch.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);status.textContent='Draft downloaded, including drawing coordinates, answers, and brief.';
    };
    submit.onclick=async()=>{
      if(busy||!room||!identity)return;
      const data=snapshot();
      if(!data.title.trim()){status.textContent='Give the idea a short title.';title.focus();return;}
      if(!data.description.trim()&&!data.strokes.length){status.textContent='Draw the idea or describe it in words.';description.focus();return;}
      if(!consent.checked){status.textContent='Confirm that you want to share this work with the classroom.';consent.focus();return;}
      persist();busy=true;submit.disabled=true;status.textContent='Saving to the classroom…';
      try{
        const r=await fetch(endpoint+'/api/submit',{method:'POST',credentials:'omit',headers:{'Content-Type':'application/json','X-Participant':identity},body:JSON.stringify({room,sketch:data,consent:true}),signal:AbortSignal.timeout(15000)});
        if(!r.headers.get('content-type')?.includes('application/json'))throw Error('The gallery needs access or is unavailable. Ask the presenter to check its sharing settings.');
        const response=await r.json();if(!r.ok)throw Error(response.error||'Could not submit.');
        status.textContent='Saved to the classroom gallery. Submit again to update this idea before voting opens.';
      }catch(e){status.textContent=(e.name==='TimeoutError'?'No save confirmation. Retrying will not create a duplicate.':e.message)+' Your draft has not been cleared.';}
      finally{busy=false;submit.disabled=!room||!identity;}
    };
    connect(window.TECHBYTES_GALLERY||'');
    document.addEventListener('workshop:links',e=>{persist();connect(e.detail.gallery);});
  }
})();
