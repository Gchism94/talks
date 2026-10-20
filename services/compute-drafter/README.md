# College of Information Science request drafting service

Optional GPT-6 Luna first drafts for public/synthetic resource needs. The existing
GitHub Pages site keeps its local template and manual campus-prompt exports.
This service uses the user's direct OpenAI API, not Arizona AI Assistant/Bedrock
credit. No automatic submission, account approval, award or staff commitment.

## Limits and key protection

- Fixed `gpt-6-luna`, reasoning none, no tools, no provider retries, 1,000 output tokens.
  Drafts target 80–110 words; schema strings and question/unknown arrays are bounded.
- JSON brief ≤6,000 UTF-8 bytes; complete provider payload ≤16,000 UTF-8 bytes.
- Shared 20 attempts/UTC day and 200/UTC month, with five/client-network/day and
  a 30-second cooldown. Networks sharing an outbound IP share this limit; this is
  an anonymous pilot, not authenticated per-person access. IPv6/proxy changes
  cannot bypass the global allowance. Origin/CORS checks are not authentication.
- Every attempt reserves $0.005 against the application allowance **before** an
  upstream call. At most $0.10/day / $1/month reserved, with margin over the
  bounded text payload at October 19, 2026 standard Luna rates ($0.10 input,
  $0.125 cache writes, $0.50 output per million tokens). Recheck prices before
  raising limits. This is this service's allowance, not an account-wide billing
  cap or guarantee against future provider price changes.
- Failures, timeouts and unreadable outputs consume an attempt. Duplicate attempt
  IDs are not called again. A new tab/redeployment/process cannot reset counters.
- Private Vercel Blob ledger uses fresh consistent reads (`useCache:false`) and
  conditional ETag writes. Only the successful writer may call OpenAI. Missing,
  corrupt or unavailable state stops generation. Never replace the ledger with an
  in-memory counter or auto-create it in a request path.
- The application persists counters, attempt UUIDs and daily HMAC network hashes,
  not prompts, drafts, names or raw IPs. Today’s hashes are retained; previous-day
  hashes are pruned on the next accepted attempt. Monthly history resets on the
  first accepted request of a new UTC month. Vercel/OpenAI process operational
  metadata under their own terms. `store:false` is requested, not zero retention.
- `OPENAI_API_KEY` and `QUOTA_HASH_SECRET` are production-only Sensitive Vercel
  variables. They are never in Pages assets or a browser. Preview generation is
  disabled. `.env*`, `.vercel`, node_modules and tests are excluded from uploads.

## Hosting and cost boundary

Dedicated Vercel project `infosci-compute-drafter`, existing `gchism94s-projects`
Pro team; no new plan/subscription was purchased. Private allowance store
`store_4wS3UJ1AuFXvHi1E` in iad1. Vercel hosting/storage operations use the existing
team's metered plan, separately from the $1 model allowance. Normal pilot traffic
is small; the model caps do not cap all infrastructure charges under arbitrary
traffic. Keep the team's existing spend controls and firewall protections, and
pause this project if unwanted traffic appears. Do not change account-wide spend
settings or other projects as part of this service.

## Build, verify and release

1. `npm ci --ignore-scripts`, `npm test` in this directory (Node 22 in production).
2. Sync `data/inventory.json` from the canonical
   `site/compute-guide/working-group.json` via the guide builder. Only public,
   dated inventory fields are used; client-supplied prompts/models are rejected.
3. Link to the dedicated Vercel project. Create/connect a **private** Blob store
   for production/development only. Keep all local environment files ignored and
   mode 600. The root credential file is outside this deployment directory.
4. Initialize the ledger **once**, with `node --env-file=.env.local init-ledger.mjs`.
   Existing state is never overwritten. Do not reinitialize for a redeployment,
   rollback, failed test or ordinary month change. Losing/deleting state requires
   usage reconciliation before reopening paid generation.
5. Set production Sensitive secrets through stdin or a secret manager. Never
   put values in command arguments, generated files, logs or chat. `ALLOWED_ORIGIN`
   is `https://gchism94.github.io`; `DRAFTING_ENABLED=true` activates paid calls.
6. Deploy this directory only. Test blocked inputs without model calls, one
   synthetic end-to-end generation and a replay of its UUID (must return 409).
   Check live ledger counters without printing network hashes or tokens.
7. Publish the matching front-end endpoint only after acceptance. Test consent,
   stale output invalidation, quota/provider failure fallback and mobile layout.

## Stop and recover

Pause **this project** in Vercel for immediate shutdown. Set
`DRAFTING_ENABLED=false` and redeploy to leave the endpoint available but paused.
Environment changes require a new deployment. Revoke this application's OpenAI
key if it is compromised; do not expose it in the browser as a workaround.
Keep the private allowance ledger through rollbacks; never delete/reset it to
recover capacity. A missing ledger deliberately disables generation. Preserve
local template and manual campus-prompt use during outages. Follow-up campus
Bedrock integration needs a campus-issued credential, verified base URL, data
terms and credit scope; no automatic fallback to a different paid model.

## Private request-review pilot (October 20, 2026)

`/api/requests` accepts an explicit, reviewed public/synthetic brief plus an
optional name and required `@arizona.edu` contact address. These are self-reported,
not verified university identities. No attachments, confidential research, student
records or other sensitive text. Preparing/downloading a brief and Luna drafting
never submits automatically. Submission has no model call or model charge.

`/review/` is the shared queue for Barney Maccabe and Greg Chism. A long shared
passphrase starts an eight-hour HttpOnly/Secure/SameSite=Strict signed session.
Review API actions require the signed session and same-origin POST, use no-store,
and never render submitted HTML. Passphrase changes invalidate all sessions.
Login attempts are persistently limited to ten per network/hour and fifty/day
shared. This is a small shared-access pilot, not NetID, individual attribution or
an approved sensitive-data intake system. The passphrase must be shared privately;
no invitation/email is sent by this application. Sign out on shared computers.

Queue storage is a **separate private Blob** (`compute-requests/queue-v1.json`),
initialized explicitly once with `node --env-file=.env.local init-intake.mjs`.
Never reset it during a release. Fresh identity-encoded reads preserve strong ETags; conditional writes protect both
submission counters and reviewer changes. Revision conflicts require refresh.
Missing/corrupt state closes intake. No queue content is copied into Pages,
repository, logs, AI prompts or review bundles. The application now persists
submitted briefs/contact/review notes in this queue; the **drafting endpoint**
continues not to persist prompts/drafts. Hosting-provider terms still apply.

Limits are three submissions/network/day, twenty shared/day, one hundred/month,
and one hundred stored requests. JSON bodies are at most 24 KB, brief text 14 KB,
review notes 3 KB. These keep the small queue bounded; they do not cap arbitrary
hosting traffic charges. No new subscription, database or email service is used.
Vercel Blob/function operations remain metered under the existing plan, separately
from the model allowance: https://vercel.com/docs/vercel-blob/usage-and-pricing.

UUID retries return the same reference without a second record. Edited payloads
require a new ID. If a response is interrupted, keep the brief unchanged and use
the same page to retry. Reviewer updates do not send emails or submit allocations.
Statuses are New, Reviewing, Needs follow-up and Closed. CSV/JSON exports include
**all** current requests, regardless of the visible filter; downloaded files contain
contact details and should be stored privately. CSV neutralizes spreadsheet formulas.
Deletion removes contact, brief and notes from the application queue; a keyed
fingerprint and reference remain until the next accepted submission in a new UTC
month for duplicate prevention. Provider retention and existing downloaded exports
are outside this deletion. No automatic deletion schedule or backup/restore is
configured: reviewers should delete entries when no longer needed and keep any
necessary authorized decision export separately. Do not promise recovery.

Production-only variables: INTAKE_ENABLED, REVIEW_ORIGIN, REVIEW_PASSPHRASE,
REVIEW_SESSION_SECRET. Credentials are in the Git-ignored, owner-readable file
`/Users/gregchism/dev/talks/.env.review`. Share only REVIEW_PASSPHRASE with Barney;
never share REVIEW_SESSION_SECRET. No secret is in a URL, browser asset or bundle.
Pause intake by setting INTAKE_ENABLED=false and redeploying; preserve queue and
AI allowance. Pausing intake also closes reviewer API until explicitly reopened.
