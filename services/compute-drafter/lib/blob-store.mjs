import { get,put,BlobPreconditionFailedError } from '@vercel/blob';
export const LEDGER_PATH='compute-drafting/allowance-v1.json';
export const blobStore={
 async read(){
  const r=await get(LEDGER_PATH,{access:'private',useCache:false,headers:{'Accept-Encoding':'identity'},abortSignal:AbortSignal.timeout(6000)});
  if(!r||r.statusCode!==200||!r.blob.etag||r.blob.etag.startsWith('W/'))return null;
  return {etag:r.blob.etag,value:JSON.parse(await new Response(r.stream).text())};
 },
 async compareAndSet(etag,value){
  try{await put(LEDGER_PATH,JSON.stringify(value),{access:'private',addRandomSuffix:false,allowOverwrite:true,ifMatch:etag,contentType:'application/json',abortSignal:AbortSignal.timeout(6000)});return true;}
  catch(e){if(e instanceof BlobPreconditionFailedError)return false;throw e;}
 }
};
