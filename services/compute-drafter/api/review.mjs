import { makeIntakeHandler } from '../lib/intake.mjs';
import { intakeStore } from '../lib/intake-store.mjs';
export default makeIntakeHandler({store:intakeStore,review:true});
