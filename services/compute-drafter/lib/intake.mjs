import { createHmac, createHash, timingSafeEqual, randomBytes } from 'node:crypto';
import { isIP } from 'node:net';
import { ServiceError, buildPayload } from './contracts.mjs';
export const INTAKE_PATH='compute-requests/queue-v1.json';
export const INTAKE_LIMITS={daily:20,monthly:100,perNetworkDaily:3,capacity:100,maxBodyBytes:24000};
export const emptyQueue=()=>({version:1,records:[],month:'',day:'',receipts:[],networks:{},loginDay:'',loginCount:0,loginNetworks:{}});
const fail=(status,message)=>{throw new ServiceError(status,message);};
const hash=(s,key)=>createHmac('sha256',key).update(s).digest('hex');
const equal=(a,b)=>timingSafeEqual(createHash('sha256').update(a).digest(),createHash('sha256').update(b).digest());
const uuid=s=>typeof s==='string'&&/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(s);
export async function queueAtomic(store,mutate){
 for(let i=0;i<6;i++){
  const r=await store.read();const q=r?.value;
  if(!q||q.version!==1||!Array.isArray(q.records)||q.records.length>100||!Array.isArray(q.receipts)||q.receipts.length>100||!q.networks||!q.loginNetworks||!Number.isInteger(q.loginCount)||q.records.some(x=>!uuid(x.id)||!Number.isInteger(x.revision)||typeof x.text!=='string'))fail(503,'The review queue is unavailable. Keep your downloaded brief and try later.');
  const before=JSON.stringify(q),result=mutate(q);
  // Receipts are read-only: do not overwrite an identical Blob for an idempotent retry.
  if(JSON.stringify(q)===before)return result;
  if(await store.compareAndSet(r.etag,q))return result;
 }
 fail(503,'The queue is busy. Keep your brief and try again shortly.');
}
function validate(body){
 if(!body||typeof body!=='object'||Array.isArray(body)||Object.keys(body).some(k=>!['brief','text','name','email','consent','requestId','website'].includes(k)))fail(400,'Invalid submission.');
 if(body.consent!==true||body.website!=='')fail(400,'Confirm permission to store and review your brief.');
 if(!uuid(body.requestId))fail(400,'A submission reference is required.');
 if(typeof body.name!=='string'||body.name.length>100||/[\x00-\x1f]/.test(body.name)||typeof body.email!=='string'||body.email.length>120||! /^[a-z0-9.!#$%&'*+/=?^_`{|}~-]+@arizona\.edu$/i.test(body.email))fail(400,'Use your University of Arizona email address.');
 if(typeof body.text!=='string'||body.text.trim().length<40||Buffer.byteLength(body.text)>14000||/[\x00-\x08\x0b\x0c\x0e-\x1f]/.test(body.text))fail(400,'Use a brief between 40 and 14,000 characters.');
 // Reuse bounded brief validation only. This never calls a model or reserves AI allowance.
 const a=body.brief;buildPayload({brief:a,consent:true,requestId:body.requestId});
 if(a.illustrative_example)fail(400,'Examples cannot be submitted. Clear the example and prepare your own brief.');
 return {name:body.name.trim(),email:body.email.toLowerCase(),text:body.text.trim(),brief:structuredClone(a)};
}
function network(req,env){const ip=env.VERCEL_ENV?req.headers['x-vercel-forwarded-for']:req.socket?.remoteAddress;if(typeof ip!=='string'||!isIP(ip))fail(503,'The submission usage check is unavailable.');return ip;}
async function json(req){
 if(!/^application\/json(?:\s*;|$)/i.test(req.headers['content-type']||''))fail(415,'Send a JSON request.');
 if(Number(req.headers['content-length']||0)>INTAKE_LIMITS.maxBodyBytes)fail(413,'Shorten the brief before submitting.');
 let raw='',bytes=0;
 if(req.body!==undefined){raw=typeof req.body==='string'?req.body:JSON.stringify(req.body);bytes=Buffer.byteLength(raw);}
 else for await(const chunk of req){bytes+=Buffer.byteLength(chunk);if(bytes>INTAKE_LIMITS.maxBodyBytes)fail(413,'Shorten the brief before submitting.');raw+=chunk;}
 if(bytes>INTAKE_LIMITS.maxBodyBytes)fail(413,'Shorten the brief before submitting.');
 try{return JSON.parse(raw);}catch{fail(400,'The request could not be read.');}
}
export function makeIntakeHandler({store,env=process.env,clock=Date.now,review=false}){
 return async(req,res)=>{
  for(const [k,v] of Object.entries({'Cache-Control':'private, no-store','X-Content-Type-Options':'nosniff','Referrer-Policy':'no-referrer','X-Robots-Tag':'noindex, nofollow','Vary':'Origin'}))res.setHeader(k,v);
  const send=(s,b)=>{res.statusCode=s;res.setHeader('Content-Type','application/json');res.end(JSON.stringify(b));};
  try{
   const site=env.ALLOWED_ORIGIN||'https://gchism94.github.io',reviewOrigin=env.REVIEW_ORIGIN||'https://infosci-compute-drafter.vercel.app';
   const allowed=review?reviewOrigin:site;
   if(req.headers.origin!==allowed)fail(403,'Use the resource tool or the private review page.');
   if(!review){res.setHeader('Access-Control-Allow-Origin',allowed);res.setHeader('Access-Control-Allow-Methods','POST, OPTIONS');res.setHeader('Access-Control-Allow-Headers','Content-Type');}
   if(req.method==='OPTIONS'&&!review){res.statusCode=204;return res.end();}
   if(req.method!=='POST'){res.setHeader('Allow','POST');fail(405,'Use the submission or review controls.');}
   if(env.INTAKE_ENABLED!=='true'||(env.VERCEL_ENV&&env.VERCEL_ENV!=='production')||!env.REVIEW_PASSPHRASE||env.REVIEW_PASSPHRASE.length<24||!env.REVIEW_SESSION_SECRET||env.REVIEW_SESSION_SECRET.length<32)fail(503,'Submission is paused. Download your brief to keep a copy.');
   const body=await json(req),now=clock(),day=new Date(now).toISOString().slice(0,10),month=day.slice(0,7),secret=env.REVIEW_SESSION_SECRET;
   const cookie=value=>res.setHeader('Set-Cookie','__Host-compute-review='+value+'; HttpOnly; Secure; SameSite=Strict; Path=/; Max-Age='+(value?'28800':'0'));
   const signature=p=>hash(p,secret+env.REVIEW_PASSPHRASE);
   if(!review){
    const value=validate(body),net=hash(day+network(req,env),secret),fingerprint=hash(JSON.stringify(value),secret);
    const receipt=await queueAtomic(store,q=>{
     if(q.month!==month){q.month=month;q.receipts=[];}
     if(q.day!==day){q.day=day;q.networks={};}
     const previous=q.receipts.find(x=>x.id===body.requestId);
     if(previous){if(previous.fingerprint!==fingerprint)fail(409,'This brief changed after a submission attempt. Prepare a new submission.');return {reference:previous.reference,duplicate:true};}
     if(q.records.length>=INTAKE_LIMITS.capacity||q.receipts.length>=INTAKE_LIMITS.monthly||q.receipts.filter(x=>x.day===day).length>=INTAKE_LIMITS.daily||(q.networks[net]||0)>=INTAKE_LIMITS.perNetworkDaily)fail(429,'The small-pilot submission limit has been reached. Download your brief and contact the working-group point people.');
     const reference='CR-'+day.replaceAll('-','')+'-'+body.requestId.slice(0,8).toUpperCase();
     q.records.push({id:body.requestId,reference,created:new Date(now).toISOString(),updated:new Date(now).toISOString(),revision:1,status:'New',notes:'',...value});
     q.receipts.push({id:body.requestId,reference,day,fingerprint});q.networks[net]=(q.networks[net]||0)+1;
     return {reference,duplicate:false};
    });return send(200,{...receipt,message:'Saved for Barney Maccabe and Greg Chism to review. This is not an allocation request, approval or promise of support.'});
   }
   if(body?.action==='login'){
    if(typeof body.passphrase!=='string'||body.passphrase.length>200)fail(400,'Enter the reviewer passphrase.');
    const hour=new Date(now).toISOString().slice(0,13),net=hash(hour+network(req,env),secret);
    await queueAtomic(store,q=>{if(q.loginDay!==day){q.loginDay=day;q.loginCount=0;q.loginNetworks={};}if(q.loginCount>=50||(q.loginNetworks[net]||0)>=10)fail(429,'Reviewer sign-in is temporarily limited. Try later.');q.loginCount++;q.loginNetworks[net]=(q.loginNetworks[net]||0)+1;});
    if(!equal(body.passphrase,env.REVIEW_PASSPHRASE))fail(401,'The reviewer passphrase was not accepted.');
    const payload=Buffer.from(JSON.stringify({exp:now+28800000,nonce:randomBytes(16).toString('hex')})).toString('base64url');cookie(payload+'.'+signature(payload));return send(200,{ok:true});
   }
   const token=(req.headers.cookie||'').split(';').map(x=>x.trim()).find(x=>x.startsWith('__Host-compute-review='))?.split('=')[1]||'';
   const [p,s,...rest]=token.split('.');let session;
   try{session=JSON.parse(Buffer.from(p||'','base64url').toString());}catch{}
   if(rest.length||!p||!s||!equal(signature(p),s)||!Number.isFinite(session?.exp)||session.exp<=now||session.exp>now+28800000)fail(401,'Sign in to review requests.');
   if(body.action==='logout'){cookie('');return send(200,{ok:true});}
   if(body.action==='list'){const q=await store.read();if(!q?.value||q.value.version!==1||!Array.isArray(q.value.records))fail(503,'The queue is unavailable.');return send(200,{records:q.value.records});}
   if(!['update','delete'].includes(body.action)||!uuid(body.id)||!Number.isInteger(body.revision))fail(400,'Invalid review action.');
   if(body.action==='update'&&(!['New','Reviewing','Needs follow-up','Closed'].includes(body.status)||typeof body.notes!=='string'||Buffer.byteLength(body.notes)>3000))fail(400,'Use a review status and notes up to 3,000 characters.');
   await queueAtomic(store,q=>{const i=q.records.findIndex(x=>x.id===body.id);if(i<0)fail(404,'This request was removed. Refresh the queue.');if(q.records[i].revision!==body.revision)fail(409,'Another reviewer changed this request. Refresh before saving.');if(body.action==='delete')q.records.splice(i,1);else Object.assign(q.records[i],{status:body.status,notes:body.notes,updated:new Date(now).toISOString(),revision:body.revision+1});});
   send(200,{ok:true});
  }catch(e){send(e instanceof ServiceError?e.status:503,{error:e instanceof ServiceError?e.message:'The queue is temporarily unavailable. Keep your downloaded brief; no automatic retry will occur.'});}
 };
}
