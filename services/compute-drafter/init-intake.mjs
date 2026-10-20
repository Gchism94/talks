// Explicit one-time initialization; never recreate/reset a missing live queue in a request.
import { get,put } from '@vercel/blob';
import { INTAKE_PATH,emptyQueue } from './lib/intake.mjs';
if(await get(INTAKE_PATH,{access:'private',useCache:false}))throw Error('Queue exists; stopped without overwriting it.');
await put(INTAKE_PATH,JSON.stringify(emptyQueue()),{access:'private',addRandomSuffix:false,allowOverwrite:false,contentType:'application/json'});
console.log('Initialized empty private review queue without changing AI allowance.');
