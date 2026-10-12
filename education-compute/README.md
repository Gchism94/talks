# Teaching on Borrowed Compute

Complete local review folder, assembled October 10 and refreshed October 12, 2026.

- [Open the five-slide talk](talk/index.html)
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
| `evidence/` | 158-record reviewed ledger, detailed text audit, degree data, source verification records, and saved source snapshots |
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


The cohesive program starts at [program.html](talk/program.html), with views for administrators, faculty and course leads. It connects the unsubmitted ACCESS CPU/GPU request and conditional CloudBank concept, proposed INFO 521/LIS 671 components, hours-only staffing and weekly effort planner, thirteen planned/not-run checks, prior assessments and the complete resource/evidence library. Request and pilot brief PDFs plus text/CSV/JSON downloads are included. Greg has ten hours/week total and zero cash budget. TA/course-lead hours are separate; course leads need no salary. Any paid needs depend on confirmed eligible EduCloud grants; no college sponsor/finance role. Runnable benchmark files and a sizing helper are in `talk/benchmarks/` and the downloadable ZIP. Local controls are separate from unrun AWS/CUDA provider measurements. Public source count: 158. Read `review/validation.json` → `accessRouteRevision` for the current release.

Canonical pilot content is `../site/education-compute-pilot.json`; shared assets are beside it. Run the existing assessment/federal/resource/appendix builders, then `../scripts/build_compute_program.py` last to restore shared navigation and the deck's Sources link. Build PDFs with `../scripts/build_compute_pilot_pdfs.py` in a Python environment with ReportLab, then run `check_site.py` and refresh this package. The new PDFs and HTML are discussion drafts, not final syllabi or CV attachments. Local `evidence/pilot-research/intranet-review.txt` records the limited Comet review; private intranet material and raw captures are not published.
