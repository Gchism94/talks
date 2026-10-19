import { makeHandler } from '../lib/handler.mjs';
import { blobStore } from '../lib/blob-store.mjs';
export default makeHandler({store:blobStore});
