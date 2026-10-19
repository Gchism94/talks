# Portfolio of approaches

**Candidates for investigation, not selected investments.** Combine approaches when useful; compare their support and recurring obligations as carefully as their technical benefits.

| Approach | Opportunity | First useful test | Main dependency |
| --- | --- | --- | --- |
| Improve use of campus resources | Reduce duplicate purchases and onboarding friction | Map one research and one teaching workflow to documented campus routes | Eligibility, headroom, support and class-use terms |
| Shared RSE and technical support | Pool scarce expertise and reusable environments | Estimate a few tasks and trial a bounded support window | Named staff, existing commitments and funding; no new appointment assumed |
| Shared data and software stewardship | Reuse datasets, metadata and environments safely | Review a dataset/license and test a portable workflow | Rights, permissions, accessibility and renewal ownership |
| Allocation-backed compute service | Support larger CPU/GPU work without relying only on free tiers | Benchmark components and validate a target route | An award, operations capacity and provider terms; ACCESS pilot remains conditional |
| Efficient models and workflows | Lower unnecessary compute and improve reproducibility | Compare a smaller model, retrieval approach or checkpointed job against a quality baseline | Task-specific evaluation; savings must be measured |
| Partnerships and shared infrastructure | Connect compatible college, campus and external efforts | Define a small joint use case with an interested partner | Agreed responsibilities, access and sustainable support |
| Reusable teaching and evaluation tools | Avoid rebuilding assignment environments and grading workflows | Test exports and a synthetic class before adoption | Maintainer continuity, account terms and separate compute quotas |

## Use one comparison standard

For each candidate, document instructional/research benefit, users served, accessibility, data suitability, required effort, recurring costs, funding status, ownership and a reversible test. Do not rank options using invented cost savings or unmeasured capacity.

[Draft recommendations](recommendations.html) · [Resource inventory](inventory.html) · [Supporting compute pilot](pilot-plan.html)

## Help prepare resource requests

The [needs tool](needs.html) produces a local request draft with documented resource routes and open questions. Copy or download its public/synthetic prompt for a fuller rewrite in **[U of A GenAI](https://responsibleai.arizona.edu/tools-support/u-gen-ai)**, which advertises no-cost NetID access with early-access and data restrictions. **[AI Verde](https://cyverse.org/ai-verde)** is an alternative after access and any token budget are confirmed. This site connects to neither model service. Review the text and share it yourself only under the chosen service’s data terms.

### Browser-model assessment

Browser inference works without API keys or per-request inference fees. We tested two quantized SmolLM2 models on synthetic examples in Chromium on this machine. The 135M model invented student-record details; a 360M model produced short drafts in about 9–13 seconds, but an integrated example added an unsupported participant condition and weakened unknown-hours language. Its initial model/runtime download was about 390 MB. These examples are a small feasibility check, not a general ranking of browser models.

The integrated 360M worker generated with networking blocked after loading. That establishes local execution for that test; it does not establish reliable drafting. We have kept browser inference disabled on the public site and chosen the simpler template-plus-campus-prompt workflow. The [SmolLM2 model card](https://huggingface.co/HuggingFaceTB/SmolLM2-360M-Instruct) also advises checking generated content. Preserve original quantities, source facts and unknowns in every draft.

### GPT-6 Luna drafting test

On October 19, 2026, **GPT-6 Luna** completed three synthetic requests—data science instruction, MLIS data work and research software support—in **5.6–6.0 seconds each**. Review against supplied briefs and dated inventory facts found that all three preserved unknown costs, staffing, permissions and capacity. Drafts were 135–163 words and kept questions for resource owners separate.

**Assessment: useful first drafts with human review.** This was three examples with facts supplied, not a reliability guarantee or a matched comparison with browser models. Total usage was 4,157 input and 1,032 output tokens; estimated token charges were **about $0.001**, including reported cache writes, using [published standard rates](https://developers.openai.com/api/docs/models/gpt-6-luna). This is an estimate, not a verified invoice. No API endpoint is connected to this site, and the test establishes no operating budget or institutional approval.
