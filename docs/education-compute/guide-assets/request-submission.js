/* Explicit, non-AI pilot intake. No browser persistence or automatic submission/retry. */
(function(){
'use strict';const panel=document.getElementById('requestSubmission');if(!panel)return;
const $=id=>document.getElementById(id),submit=$('submitWorkingRequest'),consent=$('submissionConsent'),text=$('submissionText'),email=$('submissionEmail'),name=$('submissionName'),message=$('submissionStatus');let current,requestId,busy=false;
const keys=['activity','scope','stage','timing','priority','data','budget','requirements','skills','existing','collaboration','people','hours','resources','barriers','illustrative_example'];
function ready(){return !!current&&current.data==='Public / synthetic'&&!current.illustrative_example;}
function buttons(){submit.disabled=!ready()||!consent.checked||!email.validity.valid||text.value.trim().length<40||busy;consent.disabled=!ready()||busy;panel.setAttribute('aria-busy',String(busy));submit.textContent=busy?'Saving brief…':'Submit for working-group review';}
function reset(){if(busy)return;current=undefined;requestId=undefined;consent.checked=false;text.value='';buttons();$('submissionEligibility').textContent='Prepare your own public/synthetic brief to submit. Examples cannot be submitted.';}
document.addEventListener('computing-brief-invalidated',reset);
document.addEventListener('computing-brief-updated',e=>{current={};for(const k of keys)current[k]=structuredClone(e.detail[k]);requestId=crypto.randomUUID();consent.checked=false;const facts=JSON.parse($('requestResourceFacts').dataset.resources);text.value=window.WorkingGroupNeeds.requestDraft(current,facts).text;buttons();$('submissionEligibility').textContent=ready()?'Review the text below, add a contact address and confirm permission to submit.':'Submission is limited to your own public/synthetic brief. Clear examples or keep internal/restricted needs in local downloads.';});
for(const el of [text,email,name])el.addEventListener('input',()=>{requestId=crypto.randomUUID();consent.checked=false;buttons();});consent.addEventListener('change',buttons);
$('useLocalSubmission').onclick=()=>{if(!ready()||busy)return;text.value=$('workingRequestText').value;requestId=crypto.randomUUID();consent.checked=false;buttons();};
$('useLunaSubmission').onclick=()=>{if(!ready()||busy)return;const source=$('lunaDraftText');if($('lunaResult').hidden||!source.value){message.textContent='Generate and review a Luna draft first, or submit the local brief.';return;}text.value=source.value;requestId=crypto.randomUUID();consent.checked=false;buttons();};
$('clearWorkingNeed').addEventListener('click',()=>{if(busy)return;email.value='';name.value='';message.textContent='';});
submit.onclick=async()=>{
 if(submit.disabled||!ready())return;
 if(!email.reportValidity()||!text.reportValidity())return;
 const body={brief:structuredClone(current),text:text.value,name:name.value,email:email.value.trim(),consent:true,requestId,website:$('submissionWebsite').value};
 busy=true;buttons();message.textContent='Saving this reviewed brief. Keep this page open for the reference number.';
 const controls=[...document.querySelectorAll('#workingNeeds input,#workingNeeds select,#workingNeeds textarea,#workingNeeds button,#requestSubmission input,#requestSubmission textarea,#requestSubmission button,[data-working-example]')].map(el=>({el,disabled:el.disabled}));for(const {el}of controls)el.disabled=true;
 const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),29000);
 try{
  const r=await fetch(panel.dataset.endpoint,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body),credentials:'omit',cache:'no-store',redirect:'error',signal:controller.signal});const d=await r.json();
  if(!r.ok)throw Error(d.error||'Submission could not be confirmed.');
  if(!/^CR-\d{8}-[0-9A-F]{8}$/.test(d.reference))throw Error('The receipt could not be checked.');
  message.textContent='Saved for Barney Maccabe and Greg Chism. Reference: '+d.reference+'. Keep this reference and your downloaded brief. No email confirmation is sent. This is not an approval, allocation or promise of support.';
 }catch(e){message.textContent=e.name==='AbortError'?'Submission timed out and may have been saved. Keep your download. Submitting the unchanged brief again uses the same reference; nothing retries automatically.':e.message+' Keep your download. If the response was interrupted, submitting this unchanged brief again will not create a duplicate.';}
 finally{clearTimeout(timer);for(const {el,disabled}of controls)el.disabled=disabled;busy=false;consent.checked=false;buttons();}
};reset();
})();
