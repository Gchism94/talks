import { createHmac } from 'node:crypto';
import { LIMITS,ServiceError } from './contracts.mjs';
export function emptyLedger(){return {version:1,month:'',count:0,days:{},clients:{},requests:[]};}
export function reserve(ledger,{now=Date.now(),ip,secret,requestId}){
 if(!ledger||ledger.version!==1||typeof ledger.month!=='string'||!Number.isInteger(ledger.count)||ledger.count<0||!ledger.days||!ledger.clients||!Array.isArray(ledger.requests)||ledger.requests.length>LIMITS.monthly)throw new ServiceError(503,'Drafting is paused: the allowance record needs review.');
 if(!/^$|^\d{4}-\d{2}$/.test(ledger.month)||ledger.count!==ledger.requests.length||new Set(ledger.requests).size!==ledger.requests.length||Object.values(ledger.days).some(n=>!Number.isInteger(n)||n<0||n>LIMITS.daily)||Object.values(ledger.days).reduce((sum,n)=>sum+n,0)!==ledger.count||Object.values(ledger.clients).some(v=>!v||!Number.isInteger(v.count)||v.count<0||v.count>LIMITS.perIpDaily||!Number.isFinite(v.last)))throw new ServiceError(503,'Drafting is paused: its allowance record needs review.');
 const date=new Date(now).toISOString().slice(0,10),month=date.slice(0,7);
 if(ledger.month>month)throw new ServiceError(503,'Drafting is temporarily paused.');
 const next=structuredClone(ledger.month===month?ledger:emptyLedger());next.month=month;
 const client=createHmac('sha256',secret).update(date+'|'+ip).digest('hex');
 const prior=next.clients[client]||{count:0,last:0};
 if(next.requests.includes(requestId))throw new ServiceError(409,'This drafting attempt was already received. It will not be sent again automatically.');
 if(next.count>=LIMITS.monthly||(next.days[date]||0)>=LIMITS.daily)throw new ServiceError(429,'The shared drafting allowance is used up. Use the local template or campus AI Assistant.');
 if(prior.count>=LIMITS.perIpDaily||now-prior.last<LIMITS.cooldownMs)throw new ServiceError(429,'Please wait, or use the local template. Drafting is limited to five attempts per network per day.');
 next.count++;next.days[date]=(next.days[date]||0)+1;next.clients[client]={count:prior.count+1,last:now};next.requests.push(requestId);
 // Only today's rotating network hashes are needed. No prompt, draft, name or raw IP is retained.
 if(ledger.month===month&&Object.keys(next.days).length>1){const todayClients={};for(const [k,v]of Object.entries(next.clients))if(new Date(v.last).toISOString().slice(0,10)===date)todayClients[k]=v;next.clients=todayClients;}
 return next;
}
export async function reserveAtomic(store,context){
 for(let i=0;i<5;i++){
  const entry=await store.read();
  if(!entry?.etag)throw new ServiceError(503,'Drafting is paused until its private allowance record is available.');
  const value=reserve(entry.value,context);
  if(await store.compareAndSet(entry.etag,value))return;
 }
 throw new ServiceError(503,'Drafting is busy. Use the local template or try later.');
}
