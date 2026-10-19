import { isIP } from 'node:net';
import { MODEL,LIMITS,ServiceError,buildPayload,validateDraft } from './contracts.mjs';
import { reserveAtomic } from './quota.mjs';
export function makeHandler({store,env=process.env,fetchImpl=fetch,clock=Date.now}){
 return async function handle(req,res){
  res.setHeader('Cache-Control','no-store');res.setHeader('X-Content-Type-Options','nosniff');res.setHeader('Vary','Origin');
  const send=(status,body)=>{res.statusCode=status;res.setHeader('Content-Type','application/json');res.end(JSON.stringify(body));};
  const origin=req.headers.origin,allowed=env.ALLOWED_ORIGIN||'https://gchism94.github.io';
  if(origin!==allowed)return send(403,{error:'Use the College of Information Science request tool.'});
  res.setHeader('Access-Control-Allow-Origin',allowed);res.setHeader('Access-Control-Allow-Methods','POST, OPTIONS');res.setHeader('Access-Control-Allow-Headers','Content-Type');
  if(req.method==='OPTIONS'){res.statusCode=204;return res.end();}
  if(req.method!=='POST'){res.setHeader('Allow','POST, OPTIONS');return send(405,{error:'Use the drafting button in the request tool.'});}
  if(env.DRAFTING_ENABLED!=='true'||(env.VERCEL_ENV&&env.VERCEL_ENV!=='production')||!env.OPENAI_API_KEY||!env.QUOTA_HASH_SECRET||env.QUOTA_HASH_SECRET.length<32)return send(503,{error:'Luna drafting is paused. Your local template and campus prompt are available.'});
  try{
   if(!/^application\/json(?:\s*;|$)/i.test(req.headers['content-type']||''))throw new ServiceError(415,'Send a JSON brief.');
   if(Number(req.headers['content-length']||0)>LIMITS.maxBodyBytes)throw new ServiceError(413,'Shorten the brief before using Luna.');
   const ip=env.VERCEL_ENV?req.headers['x-vercel-forwarded-for']:req.socket?.remoteAddress;
   if(typeof ip!=='string'||!isIP(ip))throw new ServiceError(503,'Drafting is paused because its usage check is unavailable.');
   let raw='',bytes=0;
   if(req.body!==undefined){raw=typeof req.body==='string'?req.body:JSON.stringify(req.body);bytes=Buffer.byteLength(raw);}
   else{for await(const chunk of req){bytes+=Buffer.byteLength(chunk);if(bytes>LIMITS.maxBodyBytes)throw new ServiceError(413,'Shorten the brief before using Luna.');raw+=chunk;}}
   if(bytes>LIMITS.maxBodyBytes)throw new ServiceError(413,'Shorten the brief before using Luna.');
   let body;try{body=JSON.parse(raw);}catch{throw new ServiceError(400,'The brief could not be read.');}
   const {payload,brief,sourceIds}=buildPayload(body);
   // Commit the persistent reservation before spending. Failures and timeouts consume an attempt.
   await reserveAtomic(store,{now:clock(),ip,secret:env.QUOTA_HASH_SECRET,requestId:body.requestId});
   const upstream=await fetchImpl('https://api.openai.com/v1/responses',{method:'POST',headers:{Authorization:'Bearer '+env.OPENAI_API_KEY,'Content-Type':'application/json'},body:JSON.stringify(payload),signal:AbortSignal.timeout(20000)});
   if(!upstream.ok)throw new ServiceError(502,'Luna is unavailable. Use the local template; this attempt will not be retried automatically.');
   const draft=validateDraft(await upstream.json(),brief,sourceIds);
   send(200,{model:MODEL,draft,notice:'AI-assisted first draft. Check every claim against the sources before sharing. Nothing has been submitted.'});
  }catch(e){send(e instanceof ServiceError?e.status:503,{error:e instanceof ServiceError?e.message:'Drafting is temporarily unavailable. Your local template is still available.',...(e instanceof ServiceError&&e.diagnostic?{diagnostic:e.diagnostic}:{})});}
 };
}
