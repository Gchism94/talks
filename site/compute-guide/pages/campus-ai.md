# Arizona AI Assistant transition

**AI Verde → [Arizona AI Assistant](https://ai-assistant.responsibleai.arizona.edu/).** **Wolfgang Jetner at the Office of Responsible AI (ORAI)** is the source of this planned transition and **$200/month of AWS Bedrock credit**, relayed by Greg Chism. Transition date, who receives the credit, eligibility, renewal and overage controls need confirmation. This is an October 19, 2026 working-group update, not a verified entitlement for every faculty member or student.

Public [university news](https://news.arizona.edu/employee-news/guide-ai-tools-u) describes Arizona AI Assistant as a fall pilot and AI Verde separately. The new portal returned HTTP 200; we have not tested a signed-in account or campus API. Contact the [Office of Responsible AI](https://responsibleai.arizona.edu/) for current enrollment and credit terms; Mithun Paul (mithunpaul@arizona.edu) is the previously published AI Verde contact for migration questions.

## Models and prices in the supplied screenshot

USD per **one million tokens**. These are campus gateway prices in the ORAI screenshot from Wolfgang Jetner, relayed by Greg Chism, not direct OpenAI prices or measured bills. Check current account rates before use.

| Model ID | Input | Output |
| --- | ---: | ---: |
| `gpt-5.6-luna` | $0.22 | $1.32 |
| `gpt-5.6-sol` | $4.40 | $22.00 |
| `gpt-6.1-sol` | $2.20 | $11.00 |
| `claude-haiku-4-5-20251001` | $1.10 | $5.50 |
| `claude-opus-5` | $5.50 | $27.50 |
| `claude-opus-5-5` | $4.40 | $22.00 |
| `claude-sonnet-5` | $2.20 | $11.00 |
| `gpt-5.6-terra` | $2.20 | $13.20 |
| `gpt-6-luna` | $0.11 | $0.55 |
| `claude-haiku-5-5` | $0.11 | $0.55 |
| `claude-sonnet-5-5` | $2.20 | $11.00 |
| `google.gemma-4-31b` | $0.14 | $0.40 |

[View supplied pricing screenshot](guide-assets/campus-ai-pricing-2026-10-19.png) · Received October 19, 2026; capture and effective dates are unconfirmed.

For example, at the listed campus Luna rate, **10,000 input + 1,000 output tokens = $0.00165** before any other charges. This is illustrative arithmetic, not an observed bill or promised credit balance. Credit provides model inference, not a reserved GPU, training cluster or guaranteed class concurrency.

## Before relying on the replacement

- Confirm migration timing, existing team/workspace exports, API compatibility and the correct API base URL.
- Confirm whether $200/month is per person, team or another allocation; determine reset, expiry and overage behavior.
- Review allowed data, retention, model availability and throughput under campus terms.
- Test one public/synthetic workflow and a classroom rehearsal before required use.

The [resource request tool](needs.html) currently uses the separate direct OpenAI Luna pilot. Its $1 monthly application allowance does not draw from campus Bedrock credit. Campus integration needs a campus-issued credential and confirmed API terms.

[Resource inventory](inventory.html) · [Drafting assessment](approaches.html)
