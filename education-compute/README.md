# College of Information Science computing resources

Complete local review snapshot. `talk/index.html` opens the resource overview; the original presentation is `talk/talk.html`, linked under Supplement. Start with the current resource guide:

- [Overview](talk/index.html): resources, the growing gap and the opportunity.
- [Resources](talk/inventory.html): contacts, access, costs and limitations.
- [Primers](talk/primers.html): six working-group discussion starting points.
- [Resource tool](talk/needs.html): local needs/request briefs and optional consented Luna drafting.
- [Report](talk/report.html): the structured current assessment.
- [Supplement](talk/supplemental.html): working materials, platform references, the conditional instructional pilot, source evidence and the talk.

Barney Maccabe and Greg Chism, Faculty Director of Instructional Computing, are the working-group point people. The original 181-record evidence ledger and full chronological audit remain saved. Keep the entire `talk/` folder together; external sources and optional Luna need internet. No credential files belong in this snapshot.

Canonical content lives in `../site/compute-guide/`, builders in `../scripts/`, public export in `../docs/education-compute/`. This folder is a gathered review copy, not the authoring directory. Read [AGENTS.md](AGENTS.md) for current editing boundaries and `review/validation.json` for release evidence; the current simplification is `focusedResourceSiteExtension`.

Refresh with `python3 scripts/package_compute_review.py` from the parent repository, then run `python3 education-compute/verify_bundle.py --compare-originals`. The review includes the appendix, runnable benchmarks and portable ZIP, not a confirmed allocation or classroom deployment.

<details><summary>Earlier assembly notes and updates</summary>

# Teaching on Borrowed Compute

Complete local review folder, assembled October 10 and refreshed October 12, 2026.

- [Open the five-slide talk](talk/talk.html)
- [Open the saved evidence appendix](talk/evidence.html)
- [Compare all nine degrees](talk/degree-options.html)
- [Compare Codabench and classroom alternatives](talk/classroom-resources.html)
- [Explore the federal-compute map](talk/federal-compute.html)
- [Download the federal comparison CSV](talk/federal-compute.csv)
- [Read the repository continuity plan](talk/repository-plan.html)
- [Read the full research audit](evidence/research-and-sources.txt)
- [Read the agent review context](AGENTS.md)
- [Portable ZIP](teaching-on-borrowed-compute.zip)

Open `talk/index.html` in a browser. Keep the entire `talk/` folder together: slides, figures, fonts, interactive controls, and appendix work offline; following external source links needs internet. Forward navigation reveals text groups before advancing; backward navigation reverses them. The appendix is saved as `talk/evidence.html`, with its structured ledger beside it in `talk/evidence.json`.

## Folder map

| Folder | Contents |
| --- | --- |
| `talk/` | Portable shareable deck, appendix, degree comparison, repository plan, assets, and evidence ledger |
| `source/` | Authored deck with presenter notes and cover |
| `evidence/` | 181-record reviewed ledger, detailed text audit, degree data, source verification records, and saved source snapshots |
| `review/` | Validation and release records, screenshots, exact published HTML exports, checks, builders, and historical authoring helpers |
| `manifest.json` | Original path, size, and SHA-256 for every gathered artifact |

The local snapshots include all files from `output/education-compute/` except the portable folder (placed under `talk/`) and the whole-site `site-build/` cache, which contains unrelated talks. New source captures and rendered Lightning pricing evidence are in `evidence/codabench-research/`; federal-map research/captures are in `evidence/federal-research/`. Related screenshots and the publishing builders are included too. Evidence records link to all cited sources; full webpage snapshots exist only where they were saved during research.

## Publication and freshness

The published talk is [here](https://gchism94.github.io/talks/education-compute/), and the published appendix is [here](https://gchism94.github.io/talks/education-compute/evidence.html). The original assembly captured release `2fe7387`. The October 11 refresh adds the Codabench correction, 13 resource comparisons and a CodaLab transition milestone. Read the latest nested record in `review/validation.json` for its validation and publication status; earlier release records are historical.

This is a review snapshot. Canonical authoring remains `../education-compute.html`; canonical public exports remain `../docs/education-compute/`; builders remain `../scripts/`. Future edits to those paths do not automatically update this folder. Its `.gitignore` keeps the local snapshot, raw provider contents, and presenter materials out of an accidental public commit; the guide, agent context, and integrity checker remain visible to Git.

Run `python3 education-compute/verify_bundle.py` from the parent `talks/` folder to check saved artifacts and their portable ZIP. Add `--compare-originals` to detect drift from the original paths. These checks verify the saved bundle; they do not revalidate provider policies or deployment.

Refresh the portable ZIP and this snapshot with `python3 scripts/package_compute_review.py` after updating canonical sources, generated references and validation records.

The October 12 federal reference maps 32 service/platform/funding families, six named IDSS projects and eight missing layers. The latest `federalExtension` record in `review/validation.json` holds verification/publication status. Federal grant provenance is distinct from current operating funding, state TRIF subsidies, no-cost access and tested production readiness.

The October 12 follow-on assessment is saved as [classroom-assessment.html](talk/classroom-assessment.html). It includes seven route/operations roles, an interactive two-course capacity model, seven unconfirmed readiness gates, and draft provider questions. Structured assessment and capacity/readiness CSVs are beside it. Public documentation captures and access checks are in `evidence/assessment-research/`; latest validation/publication status is under `assessmentExtension`. The current route uses campus AWS only for CPU component tests, free GPU benchmarks before piloting, and ACCESS CPU/GPU allocation for classroom use; CloudBank is conditional. The assessment is not an award, signed-in entitlement check or real classroom test.


The cohesive program starts at [program.html](talk/program.html), with views for administrators, faculty and course leads. It connects the unsubmitted ACCESS CPU/GPU request and conditional CloudBank concept, proposed INFO 521/LIS 671 components, hours-only staffing and weekly effort planner, thirteen planned/not-run checks, prior assessments and the complete resource/evidence library. Request and pilot brief PDFs plus text/CSV/JSON downloads are included. Greg has ten hours/week total and zero cash budget. TA/course-lead hours are separate; course leads need no salary. Any paid needs depend on confirmed eligible EduCloud grants; no college sponsor/finance role. Runnable benchmark files and a sizing helper are in `talk/benchmarks/` and the downloadable ZIP. Local controls are separate from unrun AWS/CUDA provider measurements. Public source count: 181. Read the latest nested extension in `review/validation.json` for current validation/publication status; the runnable benchmark update is under `runnableBenchmarksExtension`.

Canonical pilot content is `../site/education-compute-pilot.json`; shared assets are beside it. Run the existing assessment/federal/resource/appendix builders, then `../scripts/build_compute_program.py` last to restore shared navigation and the deck's Sources link. Build PDFs with `../scripts/build_compute_pilot_pdfs.py` in a Python environment with ReportLab, then run `check_site.py` and refresh this package. The new PDFs and HTML are discussion drafts, not final syllabi or CV attachments. Local `evidence/pilot-research/intranet-review.txt` records the limited Comet review; private intranet material and raw captures are not published.


The October 13 site reorganization puts the problem and solution in [Overview](talk/program.html), the six-stage plan and key events in [Staged plan](talk/timeline.html), and the full research material in the separate [Report & evidence](talk/report.html) section. [research-report.html](talk/research-report.html) is a readable rendering of the entire original text audit, with section links; the evidence appendix still contains 158 records. Working downloads are in Classroom tools; Hours & funding retains the ten-hour/zero-cash constraints. Stage selection is navigation, not a completion claim. Existing page URLs and the five-slide talk remain available. Canonical views are in `../scripts/compute_program_views.py`, and timeline metadata is `site_flow` inside the pilot JSON. Latest verification/publication is under `cohesiveSiteExtension`.


The October 13 Classroom 50 assessment is at [classroom50.html](talk/classroom50.html): a workable successor for assignments, externally maintained, with unchanged Codespaces compute limits and separate Actions grading quotas. It is linked from Overview, Classroom tools and Report & evidence. Five new primary records bring the current ledger to 163 and the resource comparison to 14. The site and talk now use an InfoSci-inspired Arizona navy/red/white design with offline open-license typography. No institution-owned deployment, provider benchmark or ACCESS integration is claimed. See `classroom50ArizonaExtension` for current verification and publication.


The October 16 [Modal and similar-platform comparison](talk/serverless-compute.html) covers nine providers, recurring credits versus trials/paid usage, billing/account requirements, DS/MLIS fits and unresolved offers. Current ledger: 181 records; resource catalog: 22 comparisons. Modal remains conditional because of payment and three-seat limits; ACCESS and the zero-cash/ten-hour constraints remain. See `modalComputeExtension` in validation.json for verification/publication status.


The October 19 [main report overview](talk/report.html) summarizes available resources and status, ten selected historical changes, the separately labeled Colab observation and upcoming OSF restrictions, and the ACCESS response. It retains links to the complete research and 181-source evidence ledger. Provider availability is not classroom readiness; see `reportOverviewExtension` for checks and publication.

</details>
