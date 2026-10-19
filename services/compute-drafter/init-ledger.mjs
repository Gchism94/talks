// Explicit one-time initialization. Runtime requests never recreate a missing ledger.
import { get,put } from '@vercel/blob';
import { emptyLedger } from './lib/quota.mjs';
import { LEDGER_PATH } from './lib/blob-store.mjs';
if(await get(LEDGER_PATH,{access:'private',useCache:false}))throw Error('Allowance ledger already exists; initialization stopped without overwriting it.');
await put(LEDGER_PATH,JSON.stringify(emptyLedger()),{access:'private',addRandomSuffix:false,allowOverwrite:false,contentType:'application/json'});
console.log('Initialized private allowance ledger without overwriting any existing record.');
