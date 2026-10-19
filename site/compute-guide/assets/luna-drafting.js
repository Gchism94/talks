/* Optional, explicit server-side drafting. No key, local storage or automatic model call. */
(function(){
'use strict';
const panel=document.getElementById('lunaDrafting');if(!panel)return;
const run=document.getElementById('generateLunaDraft'),consent=document.getElementById('lunaConsent'),status=document.getElementById('lunaStatus'),result=document.getElementById('lunaResult'),output=document.getElementById('lunaDraftText'),save=document.getElementById('downloadLunaDraft');
let current,revision=0,busy=false,controller;
function allowed(){return !!current&&current.data==='Public / synthetic'&&consent.checked&&!busy&&!!panel.dataset.endpoint;}
function buttons(){run.disabled=!allowed();consent.disabled=!current||current.data!=='Public / synthetic'||busy;}
function reset(){revision++;controller?.abort();controller=undefined;current=undefined;busy=false;consent.checked=false;result.hidden=true;output.value='';save.disabled=true;buttons();status.textContent='Prepare a public/synthetic brief first. Luna drafting is optional.';}
document.addEventListener('computing-brief-invalidated',reset);
document.addEventListener('computing-brief-updated',e=>{current=structuredClone(e.detail);buttons();status.textContent=current.data==='Public / synthetic'?'Review the brief, then confirm permission to send it for a Luna draft.':'Luna is unavailable for internal, restricted or unclassified information. The local template is still available.';});
consent.addEventListener('change',buttons);
run.addEventListener('click',async()=>{
 if(!allowed())return;
 const version=revision;busy=true;buttons();result.hidden=true;save.disabled=true;status.textContent='Drafting with Luna… Your brief has been sent for this requested rewrite. Nothing will be submitted to the working group.';
 const brief={};for(const key of ['activity','scope','stage','timing','priority','data','budget','requirements','skills','existing','collaboration','people','hours','resources','barriers','illustrative_example'])brief[key]=current[key];
 controller=new AbortController();const activeController=controller;const timer=setTimeout(()=>activeController.abort(),29000);
 try{
  const response=await fetch(panel.dataset.endpoint,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({brief,consent:true,requestId:crypto.randomUUID()}),signal:activeController.signal,credentials:'omit',cache:'no-store',redirect:'error'});
  const body=await response.json();if(version!==revision)return;
  if(!response.ok){const error=Error(body.error||'Drafting is unavailable. Use your local template.');error.userFacing=true;throw error;}
  const d=body.draft;if(body.model!=='gpt-6-luna'||!d||typeof d.draft!=='string'||d.ready_for_submission!==false||!Array.isArray(d.unknowns)||!Array.isArray(d.owner_questions)||!Array.isArray(d.source_ids)){const error=Error('The draft could not be checked. Use your local template.');error.userFacing=true;throw error;}
  output.value=['COLLEGE OF INFORMATION SCIENCE | AI-ASSISTED RESOURCE REQUEST DRAFT',d.illustrative_example?'Illustrative example — not a collected need':'Self-reported planning input — not a college-wide finding','GPT-6 Luna · Human review required · Not submitted',d.title,d.draft,'UNKNOWNS',...d.unknowns.map(x=>'- '+x),'QUESTIONS FOR RESOURCE OWNERS',...d.owner_questions.map(x=>'- '+x),'SUPPLIED RESOURCE IDS: '+d.source_ids.join(', '),'Check dated resource facts in the local template and inventory. Unknowns and access need owner confirmation.'].join('\n\n')+'\n';
  result.hidden=false;save.disabled=false;status.textContent='Luna draft ready. Check and edit every claim against the source-backed template before sharing. Nothing has been submitted to the working group.';output.focus();
 }catch(e){if(version!==revision)return;status.textContent=e.name==='AbortError'?'Drafting timed out. The attempt may have used allowance; it will not retry automatically. Your local template is available.':e.userFacing?e.message:'Luna could not be reached. Use your local template or a campus AI tool.';}
 finally{clearTimeout(timer);if(version===revision){busy=false;controller=undefined;consent.checked=false;buttons();}}
});
save.addEventListener('click',()=>{if(!current||save.disabled)return;const url=URL.createObjectURL(new Blob([output.value],{type:'text/plain'})),a=document.createElement('a');a.href=url;a.download='computing-resource-request-luna-draft.txt';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});
reset();
})();
