# Resource-request drafting notes

Supporting assessment of the request tool. Start with the [resource tool](needs.html) for use, or the [report](report.html) for the main findings.

## Help prepare resource requests

The [needs tool](needs.html) offers a source-backed local template and an optional **GPT-6 Luna** rewrite after explicit consent for public/synthetic information. Luna uses a server-side credential and a shared allowance: 20 attempts/day, 200/month, five/network/day, up to 1,000 output tokens each. Attempts reserve $0.005 of the application allowance before calling the model, limiting this service to $1/month in reservations at current verified rates. This is separate from account-wide billing and hosting. Failed or timed-out calls are not retried automatically.

For a manual campus route, use [Arizona AI Assistant](https://ai-assistant.responsibleai.arizona.edu/). Wolfgang Jentner at ORAI reports an AI Verde transition and $200/month of Bedrock credit, relayed by Greg Chism; [review the credit boundaries and supplied model rates](campus-ai.html). [U of A GenAI](https://responsibleai.arizona.edu/tools-support/u-gen-ai) remains another documented route. Campus API integration and credit use have not been tested here.

### Browser-model assessment

Browser inference works without API keys or per-request inference fees. We tested two quantized SmolLM2 models on synthetic examples in Chromium on this machine. The 135M model invented student-record details; a 360M model produced short drafts in about 9–13 seconds, but an integrated example added an unsupported participant condition and weakened unknown-hours language. Its initial model/runtime download was about 390 MB. These examples are a small feasibility check, not a general ranking of browser models.

The integrated 360M worker generated with networking blocked after loading. That establishes local execution for that test; it does not establish reliable drafting. Browser inference remains disabled on the public site. The local template, optional hosted Luna draft and manual campus prompt are separate routes. The [SmolLM2 model card](https://huggingface.co/HuggingFaceTB/SmolLM2-360M-Instruct) also advises checking generated content. Preserve original quantities, source facts and unknowns in every draft.

### GPT-6 Luna drafting test

On October 19, 2026, **GPT-6 Luna** completed three synthetic requests—data science instruction, MLIS data work and research software support—in **5.6–6.0 seconds each**. Review against supplied briefs and dated inventory facts found that all three preserved unknown costs, staffing, permissions and capacity. Drafts were 135–163 words and kept questions for resource owners separate.

**Assessment: useful first drafts with human review.** This was three examples with facts supplied, not a reliability guarantee or a matched comparison with browser models. Total usage was 4,157 input and 1,032 output tokens; estimated token charges were **about $0.001**, including reported cache writes, using [published standard rates](https://developers.openai.com/api/docs/models/gpt-6-luna). This is an estimate, not a verified invoice. That initial test established no institutional approval or college operating budget. The subsequent optional integration has its own usage limits and deployment checks.

## Optional submission and review

The resource tool now has a separate, explicit submission step. Public/synthetic briefs and contact details can be stored in a private pilot queue for Barney and Greg, using the existing hosting. Luna drafting never submits automatically and contact details are not sent to the model. Reviewers use a shared passphrase, update status and notes, export requests, and delete entries when no longer needed. This is not NetID, a sensitive-data intake or an allocation application.
