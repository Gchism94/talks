RUNNABLE EDUCATION COMPUTE COMPONENT BENCHMARKS
Greg Chism / UArizona Information Science | 12 October 2026

Purpose: measure DS and MLIS components before sizing an ACCESS CPU/GPU request.
Campus UITS/AWS is for CPU component testing only. Free Kaggle/Colab GPUs are
pre-pilot measurement tools; ACCESS remains the classroom CPU/GPU route.
No provider account, paid API, dataset download or resource provisioning is in
these tools. Use only an already-authorized CPU instance; stop it per campus
instructions when done. An AWS label is operator-entered, not account proof.
No cash budget is available; any paid resource/support need awaits an eligible,
confirmed grant. Do not buy an instance, notebook upgrade or compute credits.

1. CPU tests on a campus-provided AWS Linux instance (Python 3.11+)

   python3 -m venv .venv
   .venv/bin/python -m pip install -r requirements-cpu.txt
   .venv/bin/python cpu_benchmarks.py --platform campus-aws --workload all --rows 10000 --repeats 3 --threads 2 --output results/cpu

   The dependency install requires permitted package/network access. It creates
   no AWS resource. For a local functional control, use --platform local.
   Run 1k, 10k and 100k rows separately if quota/time permit; never extrapolate
   a 1k smoke test directly to a large-memory full-course job. Each workload gets
   one warm-up and three measured fresh processes, each bounded to five minutes.
   The runner records failures and returns nonzero if any run fails.

   DS: synthetic services CSV -> missing-value cleaning with training-only
   imputation/scaling -> fixed-iteration logistic fit -> holdout accuracy ->
   exported model + identical reopened predictions.
   MLIS: synthetic catalog -> NFC/whitespace/year/subject normalization ->
   indexed SQLite queries -> normalized CSV + schema/provenance/checksums ->
   reopened database/CSV checks. No patron, donor or circulation records.
   Peak RSS includes imports and generation in a fresh process. Stage timings,
   process CPU seconds and full component wall time are separate; none are
   provider billed units. The model is deliberately small, not a complete syllabus.

2. GPU notebooks: ds-gpu-benchmark.ipynb and mlis-gpu-benchmark.ipynb

   Upload either notebook to Kaggle or free Colab. Select a GPU accelerator,
   enter the provider/quota in CFG, and run cells in order. Torch and NumPy must
   be available in the selected image; the notebook does not auto-install or
   silently fall back. No external models or datasets are downloaded.
   One warm-up + three measured runs are bounded to ten minutes total (checked
   between iterations; a hung kernel/provider disconnect may terminate sooner).
   CPU fallback is disabled: no CUDA produces a saved blocked result.

   DS GPU: synthetic tabular data -> 24/64/2 MLP training -> holdout check ->
   safe checkpoint export/reload -> resumed optimizer step -> CPU replay.
   MLIS GPU: synthetic catalog-topic vectors -> 256/64 projection -> chunked
   exact retrieval -> CPU numerical reference -> saved index/reopen check.
   MLIS is a retrieval/memory proxy, not a pretrained NLP or semantic-quality
   benchmark. Replace the proxy with an approved real assignment before claiming
   full-course demand. Warm-ups are excluded from summary maxima/medians.

   CUDA calls synchronize before timing boundaries. Record device, VRAM, FP32,
   framework/config/input hash and PyTorch allocated/reserved memory peaks.
   Allocator peaks exclude driver/context and other processes; add observed
   headroom. Host peak RSS is cumulative across a notebook process.
   Visible GPUs do not prove full physical GPU allocation. Capture actual session
   start/end, quota consumed and any charged units independently.
   Export the generated ZIP from Kaggle Output or Colab Files; then disconnect.
   Partial output may be unavailable after provider termination; checkpoint early.

Optional matched CPU controls for the GPU workloads

   If PyTorch is already available on an authorized campus CPU test image:
   python3 gpu_workloads.py --workload ds --allow-cpu --platform campus-aws --output results/matched-cpu
   python3 gpu_workloads.py --workload mlis --allow-cpu --platform campus-aws --output results/matched-cpu

   This runs the same MLP or retrieval component on CPU. Install an institution-
   approved CPU-only PyTorch wheel if needed; use the official install guidance
   and record the actual version. The default CPU cleaning/SQL runner and GPU
   training/retrieval runner measure different components: do not infer a GPU
   speedup by comparing those different workloads. CPU controls remain ineligible
   as GPU measurements. Match configurations when evaluating CPU/GPU performance.

3. Size the ACCESS request from measurements

   Copy demand-example.json to your result workspace. Replace paths with actual
   results.json files and replace unapproved example student/group/job counts.
   python3 size_access.py demand.json --output access-sizing.json

   CPU local controls and GPU CPU-only controls are rejected unless --allow-local
   is passed; that option produces an explicitly ineligible local illustration.
   Failed/warm-up rows do not enter the maximum. Missing measurements fail rather
   than imply zero GPU demand. Provider conversion is null until confirmed.
   An optional provider_conversion needs provider, unit, verified_date and
   units_per_instance_hour; this is allocated-instance billing, not a universal
   core/GPU-hour-to-ACCESS-credit rate.

   Maximum measured wall time × approved jobs/groups/repeats × allowance yields
   component residency demand. Separately add classroom session/idle/provisioning,
   staff/reruns, concurrency and storage. Do not double count active components
   already inside an allocated session. Replay on target ACCESS architecture.
   The tool always leaves submission eligibility false: complete the remaining
   resource plan/provider accounting first. Current 80-seat examples are not a
   measured college-scale allocation. No quota or reservation follows from them.

Validation scope: see the program site/review record for local results. No AWS,
Kaggle, Colab or ACCESS run is claimed by delivering these files. Locally
executed CPU controls of GPU code are not GPU performance evidence.

Primary references:
https://docs.pytorch.org/docs/stable/notes/cuda.html
https://research.google.com/colaboratory/faq.html
https://www.kaggle.com/docs/notebooks
https://allocations.access-ci.org/prepare-requests
