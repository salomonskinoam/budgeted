# Budgeted feature acquisition — general direction

Companion to [`budgeted_acquisition_proposal.md`](budgeted_acquisition_proposal.md). The proposal
says *what* the world is. This doc records *how we are thinking about it* after working through the
design — in particular, what "skill" means here, what the design target actually is, and the hard
line between what we can know before students run and what we cannot. Read this before scoring
candidate datasets or shaping cost structures.

## 1. The world, in one line
A world of tasks where a student builds a policy that, under a cost budget, decides which features to
buy per instance and then predicts — and that same policy later runs in production under the same
constraints. Real data; costs engineered on top.

## 2. Skill is *defined by* score — there is no presupposed hierarchy
The single most important correction to how we were thinking:

- **Skill = whatever scores higher. Full stop.** There is no a-priori ranking like
  "planner > greedy > naive." On a given cost-and-budget layout, cheapest-first may genuinely be the
  best strategy and an elaborate adaptive planner may waste budget and lose. If so, cheapest-first
  *is* the skilled play, and that is correct — not a failure.
- Do **not** label one strategy "strong" and another "weak" before measuring. Which family wins is
  an **output we observe**, never an input we assume.

## 3. The design target: strategy choice must move the score
What makes a good task is **not** that the fancy policy wins. It is that **different strategy
families land at clearly different scores** — the score *separates* approaches — with no single
trivial move sitting on top. The proposal's phrase for this is "different strategy families and no
single winner, so scores spread." That spread is the whole product.

## 4. The spread cannot be pre-estimated — only students reveal it
The second key correction:

- **We cannot enumerate the strategies.** Students are open-ended; the interesting attempts are
  precisely the ones we did not think of. Any basket of strategies *we* run is just our imagination,
  not the space students explore.
- Therefore the spread is an **emergent, measured property of real student rollouts** — not a number
  we compute by simulating our own portfolio. (Concretely: it looks like the
  `analysis/run*_<score>` distributions in the `multimodal_fusion` world — observed scores across
  many real runs.)
- Our design job is to create **conditions under which a spread is possible**. Whether the spread is
  **real** is only known by running students and looking at the dispersion of their scores.

## 5. What we *can* check beforehand: falsifiers, not predictions
Before spending real student runs, we can only rule candidates *out*. Passing these checks never
promises a band; failing one guarantees there isn't one.

- **Degeneracy (falsifier):** if one cheap feature (or a tiny cheap subset) already reaches near the
  ceiling score, no budget decision matters and the score cannot separate strategies. Kill the
  candidate (or redesign costs so that feature is expensive). Measurable a-priori:
  `score(best affordable single feature) / score(full panel)` near 1 ⇒ degenerate.
- **Binding (falsifier):** if the budget does not bite — budget ≈ cost-of-everything, or the
  score-vs-budget curve is already saturated at the budget, or there are too few non-redundant costly
  features — there is no decision to grade. Measurable a-priori.
- **Leakage / integrity:** the target must not be trivially defined by a buyable feature (e.g. a lab
  that *is* the label); forbidden-dir reads and budget-evasion must be blocked.
- **Anti-monoculture (falsifier):** if the *prediction* half collapses to a single dominant method,
  no strategy spread can come from modeling, and the band has nowhere to form. The canonical failure
  is **strictly-tabular data → "flatten-and-tree" (gradient-boosted trees)**: GBTs are a near
  monoculture on tabular benchmarks *and* absorb missing values natively (default-direction splits),
  so the missingness that budgeted acquisition itself creates is handled for free — killing both
  prediction-strategy and imputation-strategy diversity at once. Requirement: the input must be
  **structurally irreducible** — its best model must be a *learned representation* (CNN / transformer /
  message-passing), not engineered-summaries-plus-tree. Checkable **offline**, before any student runs,
  via a modeling bake-off: does a learned-representation model *beat* a tuned GBT by a margin? If no,
  the monoculture is confirmed and the data is disqualified. (See `README_building_the_world.md`.)
  **Empirically confirmed lesson (see §9):** we initially guessed irregular multivariate time-series
  was irreducible. It is **not** — we ran the bake-off on PhysioNet 2012 mortality and a tuned GBT on
  ~330 engineered per-channel summaries *beat* a competent GRU-D on every fold. So **time-series
  counts as tabular here**: students reduce it to summaries and tree it, and that wins. The dividing
  line is not the file format — it is "does a student's winning move reduce to summaries + GBM?"

Everything else about the band is **not** pre-checkable and must be observed.

## 6. The process
1. Pick real data with plausible conditional structure (cheap-feature-value changes which expensive
   feature is worth buying) and engineer a cost/budget layout on top.
2. Run the **falsifier checks** (degeneracy, binding, leakage). Cut anything that fails.
3. **Run real students.** Measure the dispersion of their scores. This is "measure the spread first."
4. Keep tasks where a spread emerges; cut or re-shape tasks where scores pile up at one value
   (whether that value is reached by a simple or a complex strategy — both are failures of
   discrimination).
5. The graded artifact is the same across agent-time and deferred/grader-time modes, so the mode
   switch is seamless.

## 7. Glossary (neutral definitions — no presumed winner)
For each: what it is, why it matters, how to measure, direction wanted, and whether it is
pre-checkable.

- **Spread / the band** — dispersion of *student* scores at a fixed budget. *Why:* the product.
  *Measure:* observed only, from real rollouts. *Want:* large. *Pre-checkable:* **no.**
- **Conditional structure** (was loosely "gating") — the property that the best next purchase depends
  on values already revealed, so the cost-and-data layout *can* make strategies diverge. *Why:* it is
  the structural cause that makes a spread possible. It does **not** imply the adaptive policy wins.
  *Measure:* structural / interaction presence; true effect only via students. *Want:* present.
  *Pre-checkable:* partially (structure yes; resulting spread no).
- **Degeneracy** — one cheap move already tops the score, so strategy choice stops mattering. *Why:*
  collapses the band by removing discrimination. *Measure:* best-single-feature ÷ full-panel score.
  *Want:* low. *Pre-checkable:* **yes (falsifier).**
- **Irreducibility** (anti-monoculture) — the input cannot be flattened into a tree-friendly row, so
  the prediction half has no single dominant method. *Why:* tabular data collapses to flatten-and-tree
  (a monoculture that also eats missingness for free), leaving no room for modeling/imputation strategy
  to separate. *Measure:* offline bake-off — a structure-aware model beats a tuned GBT under partial
  observation. *Want:* high. *Pre-checkable:* **yes (offline falsifier).** This demotes natively
  tabular datasets (Diabetes-130, Thyroid, NHANES-as-flat) and favors structured ones (PhysioNet,
  MIMIC, C-MAPSS).
- **Binding** — the budget is a real, biting constraint. *Why:* no decision otherwise. *Measure:*
  cost(all)/budget ≫ 1 and score-vs-budget still rising at B. *Want:* yes. *Pre-checkable:* **yes
  (falsifier).**
- **Realism** — per-feature costs correspond to something true (published price, sensor energy) rather
  than invented. *Why:* credibility and anti-gaming (stops us tuning costs just to manufacture a
  band). *Measure:* published cost table / unambiguous physical ordering exists. *Want:* more (soft,
  not a gate). *Pre-checkable:* yes.
- **Friction** — effort to obtain and prep the data (download, credentialing, ETL). *Why:* our build
  cost and shippability only; does not affect the band. *Measure:* access tier + number of
  merges/transforms. *Want:* less. *Pre-checkable:* yes.
- **Temporality** — a real time axis exists (timestamps, sequential measurements). *Why:* lets the
  `cost(f, t)` mode and deferred mode be built honestly. *Measure:* per-instance timestamps present.
  *Want:* more *if* we want the time mode; neutral otherwise. *Pre-checkable:* yes.

## 8. Status / where the dataset survey landed
We grounded 11 real candidates (each researched, not eyeballed) on the three decision-driving axes —
**Conditional** (enabler), **Degeneracy** and **Binding** (the two pre-checkable falsifiers). The
verdict below is a *screen*, applied with one rule: **cut anything that trips a falsifier we can
check now; keep the rest for students to test.** Keeping a row never promises a spread — only running
students on a concrete cost/budget layout reveals that (see §4–§5). All 11 are retained in the table
for the record; the Verdict column carries the decision.

**Legend** (↑ = higher better, ↓ = lower better):
- **Rows** — usable samples after cleaning.
- **Features** — distinct acquirable units a policy could buy.
- **Target** — prediction task type.
- **Conditional** ↑ — best next purchase depends on values already revealed (the enabler of a spread).
- **Degeneracy** ↓ — one cheap move already tops the score (pre-checkable falsifier).
- **Binding** ↑ — the budget actually bites (pre-checkable falsifier).
- **Realism** ↑ — per-feature costs are real, not invented.
- **Friction** ↓ — effort/access to obtain and prep the data.
- **Temporality** ↑ — a real time axis exists (enables the `cost(f,t)` mode).
- **Verdict** — Keep / Cut from the falsifier screen.

| Dataset | Rows | Features | Target | Conditional ↑ | Degeneracy ↓ | Binding ↑ | Realism ↑ | Friction ↓ | Temporality ↑ | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| PhysioNet'12 | 12k | 43 (~37 series) | binary | High | Low | High | High | Med | High | **Keep** — clears both falsifiers; open + time axis |
| MIMIC-IV | ~94k stays | dozens–100s | analyst | High | Med | High | High | High | High | **Keep** — high ceiling; credentialed |
| NHANES | ~9k/cycle | O(10³) tiered | analyst | High | Med | High | High | High | Med | **Keep** — tiered; ETL + leakage watch |
| Diabetes-130 | ~99k | ~13 groups | binary/3-cls | High | Low | Med | High | Low | Med | **Keep** — zero friction; modest signal |
| C-MAPSS | ~10⁴–10⁵ | 24 (14 live) | regression | High | Med | Med | Med | Med | High | **Keep** — regime structure; time axis |
| Thyroid | ~3.8k (9k pooled) | ~21 (5–6 labs) | binary/3-cls | High | Med | Med | High | Low | Low | **Keep** — native flags; borderline rows |
| PAMAP2 | ~10⁴–10⁵ | ~40 ch | 12-class | Med | **High** | Med | High | High | High | **Cut** — single IMU ~tops accuracy |
| UCI-HAR | 10,299 | 9 channels | 6-class | **Low** | **High** | Low | High | Low | Med | **Cut** — accel-only ~tops the task |
| Gas Drift | 13,910 | 16 / 128 | 6-class | **Low** | **High** | Low | Low | Low | High | **Cut** — redundant sensors; baseline leakage |
| Credit Default | 30,000 | 23 | binary | **Low** | **High** | Med | Med | Low | Med | **Cut** — PAY_0 ≈53% of decisioning |
| Adult | 48,842 | 14 | binary | **Low** | **High** | Low | Low | Low | Low | **Cut** — a few features dominate |

**Reasoning for the cull.** The four bottom rows fail *both* available falsifiers at once — no
conditional structure to make purchases matter, and a cheap subset already tops the score — so no
cost/budget layout we design could open a spread on them; they are removed. PAMAP2 has some
conditional structure but still trips degeneracy (one well-placed sensor nearly tops the array), so
it is removed on the single hard strike. The six **Keep** rows all clear both falsifiers; the
differences among them are practical — **Friction** (MIMIC/NHANES are credentialed / heavy ETL),
**Rows** (Thyroid is borderline small), and **Temporality** (PhysioNet'12 / C-MAPSS carry the real
time axis for a future `cost(f,t)` mode) — not skill-killers. Final shortlist (now obsolete, see
Update 2): **PhysioNet'12, MIMIC-IV, NHANES, Diabetes-130, C-MAPSS, Thyroid.**

**Update 1 — the Irreducibility axis reordered this.** The screen above predates the anti-monoculture
falsifier. Applying it demoted the natively tabular keeps (Diabetes-130, Thyroid, NHANES-as-flat) and
favored the "structured" ones (PhysioNet, MIMIC, C-MAPSS).

**Update 2 — PhysioNet was tested and FAILED; the whole table is now obsolete.** We ran the offline
bake-off on PhysioNet'12 (build doc §8): GBT AUPRC 0.511 vs GRU-D 0.462, GRU-D won 0/5 folds, ΔAP
95% CI [−0.081, −0.017]. Multivariate clinical time-series is a **tabular monoculture** — the tree
gets the free win. Every remaining "Keep" in this table is also tabular-or-time-series and would fail
the same way. **We are abandoning tabular/time-series data entirely** and pivoting to non-tabular
(perceptual / high-dimensional) data whose best model is a learned representation. See §9–§11 for the
new direction; this 11-dataset survey is retained only as the record of how we learned the lesson.

## 9. The data-type pivot (post-PhysioNet) — what "non-tabular" actually means
> **SUPERSEDED — read §15–§20.** §9–§14 pursued a pivot to non-tabular/perceptual data on the belief
> that static tabular acquisition could never band. §19 disproved that: high-heterogeneity many-class
> tabular (TEP) *does* band. §9–§14 are kept as the record of the perceptual detour and its lessons
> (still valid *if* we ever want a modeling-spread world); the world we actually built is tabular
> mediated-acquisition — see §20.

The PhysioNet FAIL generalizes past one dataset into a hard rule for picking data.

- **"Tabular" is a modeling outcome, not a file format.** A dataset is tabular for our purposes iff a
  student's *winning* move is **engineered summaries + gradient-boosted tree**. That is the monoculture
  that kills the band.
- **Multivariate time-series is tabular in this sense.** Students summarize each channel
  (last / mean / min / max / slope / count / time-of-last) and tree it; on PhysioNet that *beat* a
  competent GRU-D on 5/5 folds. So "it has a time axis" does **not** make it irreducible. Treat
  time-series as tabular — that is how students treat it.
- **The positive requirement:** data whose best model is a **learned representation** — a CNN over
  pixels, a transformer over language, a small conv/attention net over a spectrogram — where
  summaries+GBM *genuinely loses*. That means **perceptual / high-dimensional / structured** data.
- **The test is unchanged:** the offline bake-off (a learned-representation model must beat a tuned GBM
  on the full data). What changed is the *kind* of data we feed it.
- **Why this is a real screen, not a preference:** on perceptual data the bake-off bar is *easy* to
  clear — flattened pixels / raw waveform into a GBM is genuinely poor (it cannot see spatial or
  semantic structure), while even a tiny learned net is not. That asymmetry is exactly what was absent
  for tabular/time-series, where the GBM was already near-best.

## 10. Promising non-tabular directions (all documented; graph descoped)
Two ways a budget lands on non-tabular data:
- **Geometry A — across-source:** buy *which* rich source to acquire (modality / view / instrument).
- **Geometry B — within-signal:** buy *which parts* of one rich signal (patches / resolution of an
  image, bands of a spectrum, segments of audio, sections of a document).

Directions we are keeping (each names the data type, the acquirable unit, why it is non-tabular, and
where the conditional structure lives):

1. **Budgeted multimodal** (Geometry A) — *guaranteed to host a band.* Data = paired image + text +
   audio (+ sensor). Buy which modality to acquire per instance. Non-tabular: each modality needs its
   own encoder; fusion is non-trivial. Conditional structure: a cheap modality's content gates whether
   an expensive one adds anything. *Caveat:* overlaps the existing `multimodal_fusion` world — the
   novelty here is the **budget**, not the data, so the build reuses fusion machinery.
2. **Active visual perception / "where to zoom"** (Geometry B) — *strong real-life use case.* Data =
   images. Buy glimpses / patches / resolution tiers of a single image under a budget, then predict.
   Non-tabular: pixels need a CNN; flattened-pixels+GBM is weak. Conditional structure is *maximally*
   native — a cheap low-res gist tells you *where* to spend budget zooming, and each glimpse informs
   the next (lineage: Recurrent Attention Model, Mnih et al. 2014). Best CPU-feasible perceptual task.
3. **Within-signal audio** (Geometry B) — Data = audio clips. Buy time segments / frequency bands /
   sample-rate. Non-tabular: log-mel spectrogram → small CNN. Conditional structure: a cheap coarse
   listen gates which segment/band to analyse finely.
4. **Spectral band selection / hyperspectral** (Geometry B) — Data = hyperspectral image tiles. Buy
   spectral bands. **Caution (tabular trap):** a *per-pixel* spectrum is just a vector of band
   intensities → a GBM tree-ables it → tabular → disqualified. It is only non-tabular if the model
   uses **spatial-spectral context** (patches across bands → CNN). Keep only the spatial-spectral
   framing.
5. **Medical acquisition cascade** (Geometry A + hybrid) — *very good use case.* Data = cheap clinical
   context (vitals/tabular) plus expensive **perceptual** tests (chest X-ray, ECG/EEG waveform, a
   histopathology image). Buy which test to run. Non-tabular: the *decisive* bought feature is an
   image/signal, so it needs a learned representation. Conditional structure: cheap context gates
   whether the expensive scan is worth it. *Requirement:* the dataset must be **big enough** that the
   band has resolution (enough samples where the expensive scan flips the prediction).
6. **Hybrid: cheap-tabular → expensive-perceptual** (a *modifier* on any of the above) — keep cheap
   scalars free; make buying the rich modality (image / signal / text) cost. This **weaponizes the
   PhysioNet lesson directly**: the budget decision becomes "is it worth paying for the thing a tree
   cannot model?" — so the acquisition decision and the irreducibility requirement reinforce instead
   of fight.
7. **Budgeted document reading** (Geometry B, text) — Data = long documents. Buy which
   sections/passages to read under a **token budget**, then answer/classify. Non-tabular *iff the task
   is hard enough to defeat bag-of-words* (semantic/QA, not topic-spotting). Conditional structure:
   a cheap index (title / headings / first sentences) gates which passage to read. *CPU caveat:* needs
   a language encoder — the weakest of these on CPU (see §11). Task shape: long-document QA or
   fact-extraction where the answer lives in one of many sections, the reading budget forbids reading
   all of it, and a cheap table-of-contents pass gates which section to open. *Chooses by what:* the
   cheap observable — section headings/titles, or a cheap retrieval score over first-sentences/
   snippets, or iterative (open a passage, its content points to the next). *Existing datasets (no
   per-doc engineering):* **QASPER** (NLP papers, answers grounded in annotated paragraphs),
   **HotpotQA** (2 gold paragraphs among 10, sentence-level supporting facts), **ContractNLI**
   (contracts, evidence clauses), **Natural Questions** (Wikipedia pages, long-answer paragraph).

**Descoped: graph / relational querying.** It has arguably the *strongest* native conditional
structure (each probe reveals where to probe next), but the user has descoped it. Not pursued.

### 10-deepdive. Direction 2 (active visual zoom): what the decider predicts, the literature, and why it FAILS on CPU
We worked this one to the bottom; recording it so the analysis (and the diagnostic it yields for the
others) is not lost.

**What the acquisition decider/head predicts** (this part generalizes to any within-signal acquisition):
- *(A) Location policy* — outputs a distribution over the *next* patch/location (a categorical over
  grid cells, or a Gaussian over `(x,y)`). Selection is non-differentiable → trained with REINFORCE,
  reward = accuracy under budget. High ceiling, finicky. (RAM line.)
- *(B) Per-candidate value* — outputs one scalar per candidate = expected usefulness of buying it
  (expected uncertainty reduction / prediction improvement); greedily buy the argmax. Trainable by
  **supervised oracle-imitation**: on training data you have the full image, so measure each patch's
  true marginal contribution and regress the head to it → **no RL**. This is the lower-risk start.

**Literature (we adapt, we do not invent):** vision hard-attention / budgeted patches — RAM (Mnih
2014), DRAM (Ba 2015), Saccader (Elsayed 2019), **Glance-and-Focus (Wang 2020)** [closest to this
task], Learning When & Where to Zoom (Uzkent & Ermon 2020), Saliency Sampler (Recasens 2018), STN
(Jaderberg 2015). Active feature acquisition (the general "what to buy next" math) — **EDDI (Ma
2019)**, Joint AFA+Classification (Shim 2018), Classification with Costly Features (Janisch 2019),
Datum-wise (Dulac-Arnold 2011).

**Why zoom fails on CPU — the decider-backbone problem.** The decider must answer "where is the
discriminative detail?" *from the cheap thumbnail* — a spatial-localization job, so it needs its own
perception backbone on the thumbnail. Three fatal frictions:
1. A frozen ImageNet *classifier* backbone is the wrong tool (whole-image, ~224px); a backbone good at
   *low-res localization* would have to be trained on our data → straight back into the
   not-enough-images / not-enough-CPU problem.
2. **Localize-implies-classify:** a backbone strong enough to localize from the thumbnail can usually
   ~classify from it → no need to zoom → budget doesn't bind → band collapses. The task survives only
   in the thin gap "localizable but not discriminable at thumbnail resolution."
3. **The cost premise is artificial on small images.** Zoom exists to avoid processing everything at
   full res (pathology, satellite, gigapixel). On CPU we are forced to *small* images, where full
   processing is cheap → the acquisition cost is fake and a "downsample-and-classify the whole image"
   baseline is hard to beat. Hard-attention beats full-image baselines mainly on *large* images
   (Glance-and-Focus = ImageNet-224). So **zoom genuinely needs big images → breaks CPU-only.**

**The diagnostic this yields (applies to ALL directions): decider difficulty splits them.**
- **Within-signal acquisition** (zoom, audio segments, spectral bands): the decider must *localize
  within a rich signal* → needs its own strong perception backbone on the cheap view → hits the
  localize-implies-classify tension. **Hard.**
- **Across-source acquisition** (multimodal, medical cascade, document-by-section): the decider only
  picks among *a few discrete sources* from cheap context ("buy the X-ray?", "open which section?")
  → **no localization backbone needed**; the heavy perception lives only in the *predictor*, where a
  pretrained encoder per source is fine. **Easy.**

**Conclusion.** Zoom is **dropped for the first CPU build** — the decider-backbone requirement is the
fatal friction. This also revises §13's optimistic from-scratch framing. Favor **across-source**
directions, where the decider is a cheap few-choice head and the band comes from genuinely conditional
acquisition decisions. (Note: this reclassifies *document reading* as across-source-like — routing by
heading is a cheap discrete decider; its only hard part is the CPU language *predictor*, not the
decider.)

## 11. CPU feasibility — grounded assessment
Constraint: the proposal is **CPU-only for now**, and the student's *runner* must train its model
inside the task's compute budget. The naive intuition "perceptual data needs a GPU" comes from
training **big models on big inputs for many epochs to chase SOTA** — none of which we need. We need a
model that (a) clearly beats summaries+GBM (an *easy* bar on perceptual data) and (b) trains in
minutes-to-~an-hour on CPU. The two levers are **input size** and **model size**, both controlled by
design.

- **Images / "where to zoom" — FEASIBLE at small scale (and here is *why*, since it is counter-
  intuitive).** GPU is needed for ImageNet-scale (224px+, ResNet/ViT, millions of images, hundreds of
  epochs). Our task is the opposite on every axis: a glimpse/patch is tiny (8–32px), the predictor is
  a small CNN (a few conv layers), and we need *spread*, not 95% accuracy. Concretely a small-CNN
  forward on a 32×32×3 image is sub-millisecond per image single-threaded; training on ~50k small
  images for a few epochs is minutes-to-~1h on CPU — the same order as our own GRU-D bake-off
  (4000×48×36 ran 0.7 s/epoch single-thread). The anti-monoculture bar is *cleared even at 28–64px*
  because flattened-pixels+GBM cannot see spatial structure while a tiny CNN can. The real limit is
  **resolution/throughput**, not feasibility — we cap input size to stay on CPU.
- **Audio (within-signal) — FEASIBLE.** A 1-second clip → 64×64 log-mel → small CNN is the same order
  as small images. No GPU at this scale.
- **Spectral / hyperspectral — FEASIBLE but caveated.** Spatial-spectral CNNs on *small patches* are
  CPU-OK; the bigger risk is the tabular trap (§10.4), not compute. Moderate.
- **Multimodal — FEASIBLE at modest scale.** The existing `multimodal_fusion` world already runs
  CPU-only; keep per-modality encoders small.
- **Medical cascade / hybrid — FEASIBLE with downsampling.** Downsample the perceptual modality (e.g.
  a chest X-ray at 64–128px + small CNN). "Big enough" is about **sample count**, not per-sample
  compute, so CPU cost scales with images-per-epoch, which we control.
- **Document reading — WEAKEST on CPU.** Real language understanding wants a transformer encoder; on
  CPU you are limited to small encoders / sentence-embedding models and short-ish contexts. Feasible
  for modest tasks; genuine long-document reasoning likely wants a GPU. Honest flag: conceptually
  great, CPU-borderline.

**Direct answers to the GPU questions:** within-signal audio — *no GPU*; images/zoom — *no GPU at
small scale* (justified above); hyperspectral — *no GPU at small spatial patches*, but mind the
tabular trap; document reading — *the one that most wants a GPU*.

## 9b. Grading note — best_observed = 1 for now (no oracle normalization)
- The score normalizer **`best_observed` is fixed at 1 for every dataset until further notice.** Raw
  scores are not divided by any oracle/observed-best. (Promoting a real normalizer is a later,
  approval-gated step per `CREATING_A_WORLD.md`.)
- An informed (label-aware) oracle is a **legitimate** oracle, not garbage: e.g. the acquisition
  oracle hit ~0.98 AP on PhysioNet by choosing, per instance, which feature-reveal makes the predictor
  correct — and because the masking-trained predictor is **non-monotone**, a chosen subset *can* beat
  "buy everything." That is a valid upper bound. But it leaks the label through the *selection*, so it
  wildly overstates *deployable* skill → never use it for normalization or as the band's yardstick.
  The meaningful comparison is always the **deployable, label-free** buyers (fixed vs adaptive).

## 12. Who "the student" is, and the raw-data principle
Grounded in the existing `multimodal_fusion` world (its `prompt_builder.py` and `solution.sh`), to
remove a recurring confusion.

- **The student is an LLM coding agent.** It is told (fusion's exact contract): *"Write a Python
  script to `solution.py`. When run it must read the data and write your test predictions … Train now
  and RUN your script."* The agent **never perceives or predicts itself** — it writes code; that code
  trains the model and emits predictions. The graded artifact is the script + the model it produces.
- **The model is code-the-student-submits-trained.** For a perceptual task the predictor (and any
  acquisition net) are **DNNs trained in-rollout by the student's script, on the raw data we ship** —
  not pretrained, not provided by us (a frozen backbone is an optional knob, see §14). Training
  happens during the rollout (agent-time) or at grade time (deferred / `train_at_grade`); the model
  venv has CPU torch.
- **Ship RAW data, never pre-pooled features.** Fusion's own note: *"raw sequence … the student does
  ALL the aggregation/fusion. Un-pooled features are what create score spread."* Pre-extracted feature
  vectors = tabular = the PhysioNet collapse. So we ship raw images/audio/etc. and the student's code
  builds the representation — that *is* the task and the source of spread.

## 13. The acquisition task is multi-step — unlike fusion — and how it is trained
Fusion is **single-step supervised** (`f(x)→y`, no acquisition decision). Our world adds a
**sequential, adaptive acquisition decision** (what to buy next, under budget, conditioned on what is
seen). Fusion provides no template for this; it is the genuinely novel part. The standard, tractable
way to train it — **without RL** — is to decouple:

1. **Partial-observation predictor (supervised, single-step, fusion-like).** Train a model that
   predicts the label from *any subset* of features, via random-masking augmentation:
   ```
   for (x, y) in train:
       S = random affordable subset of features      # e.g. patches of an image
       train  predictor( features(x, S), mask(S), free_context(x) ) → y
   ```
   One forward/backward, no sequential decisions, CPU-tractable (fusion difficulty + masking).
2. **Acquisition loop (inference-time code, no training, no RL).**
   ```
   observed = {free_context}                          # e.g. a low-res thumbnail
   while budget remains:
       score(p) = expected uncertainty reduction under the predictor, for each unbought feature p
       buy argmax score; observed += that feature
   predict y = predictor(observed)
   ```
   The multi-step part is plain code over the *already-trained* predictor (lineage: EDDI / greedy
   active feature acquisition). A student *may* instead train a joint RL policy — harder, and just
   another point in the spread.

**Crisp formulation (makes "feature" concrete).** Grid an image into N patches; *"buy patch (i,j)" =
reveal it*; budget = buy k of N; a free thumbnail is the gist. This is **structurally identical to the
original tabular budgeted task** (N features, buy k, predict) — the only change is that each feature
is an image patch, so the predictor must be a CNN (→ non-tabular → passes the gate).

**Where the band lives:** (a) predictor robustness to sparse observation, and (b) acquisition-loop
quality (random/fixed vs greedy vs planned vs learned). Weak entry (fixed patches + brittle predictor)
lands low; strong entry (robust predictor + good greedy acquisition) lands high at the same budget.
**Degeneracy guard:** the signal must be *localized* so *which* features you buy matters — baseline to
run is "fixed-center patches"; if it ties the smart policy, info is not localized → reshape or reject.

## 14. The world as a task generator — the multiplier axes
The value is a *world* that emits many tasks, most as just a config + a data file (the fusion model:
one world, N dataset instances). The Cartesian product, with honest cost/value labels:

| Axis | Example values | Marginal work | Real new task vs cosmetic |
|---|---|---|---|
| **Domain / dataset** | birds, aircraft, cars, X-ray, satellite, doc-images | **cheap** (config + data) | **Real** — signal localizes differently per domain |
| **Acquisition geometry** | spatial patches · resolution tiers · spectral bands · modalities · audio segments · doc sections | **medium** (new primitive each) | **Real** — different acquisition skill |
| **What the student trains** | both · predictor-only (frozen acq.) · acquisition-only (frozen predictor) | medium (ship frozen part) | **Real** — isolates a different skill |
| **Adaptivity** | one-shot subset vs sequential adaptive | medium | **Real** — conditional structure lives here |
| **Budget / cost** | buy k of N; uniform vs per-feature cost; per-sample vs total; `cost(f,t)` | **cheap** (config) | Moderate — related difficulty points |
| **Target / metric** | classification · fine-grained · regression · count | cheap if labels exist | Real-ish |
| **Mode** | agent-time vs deferred (`train_at_grade`); `cost(f)` vs `cost(f,t)` | **cheap** (SDK flag) | Cheap, already supported |

**Cheap-breadth recipe:** a few *harness-level* primitives (geometry × adaptivity × what-student-
trains) each open a cheap *config plane* (dataset × budget × mode). Build one primitive (spatial
patches + greedy-adaptive + train-both) → get dataset×budget×mode ≈ 20 candidate tasks for almost no
marginal work; add a second geometry → another plane.

**Honest caveat:** the product generates **candidates, not keepers.** Many cells collapse (budget too
loose, signal not localized, greedy ≈ random). The cheap multiplier buys *breadth to screen*; the
ongoing labor is **curation** — run the falsifiers + measure the spread per cell, keep the ones that
separate. "Measure the spread first," applied across a grid.

## 15. Two sources of band — and we over-pivoted
A band can come from **either** half of the task, and we conflated them:
1. **Modeling spread** — different students build different *predictors*. Needs non-tabular data
   (§5 anti-monoculture, §9). This is the branch §9–§14 pursue.
2. **Acquisition spread** — different students build different *routing/planning policies*. Here the
   predictor can be a plain GBM and it doesn't matter; what's needed is **conditional structure so an
   adaptive policy beats a fixed panel** (the proposal's original "planner beats greedy" thesis).

The anti-monoculture bake-off tested only the **predictor** (unbudgeted). It said nothing about
acquisition. So "abandon tabular" (§8 Update 2) was correct **for modeling reasons only** — tabular
is still a live substrate for the **acquisition-spread** branch. §16 tests that branch.

## 16. The acquisition-spread gate — results, and the target lesson
**The gate (analogue of the bake-off, for the acquisition branch).** On a tiered-cost tabular dataset,
share ONE masking-robust predictor and compare label-free buyers at a fixed budget:
`random` · `fixed-best` (one forward-selected panel for all instances) · `eddi-adaptive` (VoI by
imputation-sampling) · `peek-adaptive` (optimistic, uses realized values, still no label). Read:
**adaptive ≫ fixed → per-instance adaptivity matters → acquisition band**; **adaptive ≈ fixed →
monostrategy** (the task is just "pick the best fixed panel" = feature selection everyone converges
to). The label-aware oracle is *not* used (§9b).

**Results — both current tabular candidates FAIL, in opposite ways** (AUPRC):

| Dataset (tiers) | free | full | random | fixed-best | eddi-adap | peek-adap | verdict |
|---|---|---|---|---|---|---|---|
| **PhysioNet** vitals/labs @B=6 | 0.247 | 0.519 | 0.274 | **0.415** | 0.401 | 0.417 | selection matters, **adaptivity doesn't** |
| **Diabetes-130** multi-tier @B=3 | 0.130 | 0.246 | 0.211 | 0.246 | 0.246 | 0.246 | **budget doesn't even bind** |

- **PhysioNet:** labs *do* help (full ≫ free) but their value is **global, not conditional** → a fixed
  cheap panel is optimal → adaptivity (even optimistic peek) gives nothing.
- **Diabetes-130:** a budget-3 cheap panel already equals *buying everything* → the expensive labs
  (A1C/glucose) add **nothing** → no acquisition problem at all.

**The target lesson (the fundamental error Diabetes-130 exposed).** Why would expensive tests have ~0
predictive power? Because **we used the wrong target.** A1C/glucose are expensive since they are
**diagnostic/therapeutic for diabetes**, not predictive of **30-day readmission** — a noisy downstream
outcome driven mostly by prior-utilization history. Aiming the labs at readmission made them look
worthless. **Principle: the target must be the thing the expensive tests diagnose.** Downstream
outcome targets (mortality, readmission) sit below many causes and wash out any single test's value;
**diagnosis targets** put it front and center. Corollary: for an acquisition band we want **multi-class
DIAGNOSIS targets where the decisive expensive test is class-specific (conditional)** — binary
low-signal outcomes (mortality/readmission) structurally cannot have it (one global boundary → global
relevance → fixed panel wins).

**Next test — Thyroid (multi-class diagnosis).** Fits the refined requirement: target = 3-class
diagnosis (normal/hypo/hyper); decisive labs are **class-specific** (TSH screens; T3/T4/FTI confirm
hypo vs hyper); native cost tiers (free clinical/history + expensive assays). The hypothesis: TSH
result gates *which* follow-up assay is worth buying → adaptive beats a fixed panel.

**Watch: TSH-degeneracy.** TSH may be near-sufficient alone → fixed `{TSH}` wins → no band (same
failure family). Mitigations if TSH is too predictive too early:
- **price-gate it** — make TSH costly so buying it is itself a real budget decision;
- **remove it** — force students onto T3/T4/FTI and the clinical features;
- **add noise** — inject measurement noise into TSH. This is *clinically realistic*: normal-range TSH
  routinely coexists with symptomatic patients, so noisy TSH reflects reality, not just difficulty.

**Thyroid RESULT — fails too.** High-signal, so the target is right (free clinical ≈ chance 0.36;
full labs bAcc 0.988). But **fixed-best wins at every budget** (fixed-best@3 = 0.801 from TSH alone;
@6 = 0.974); adaptive (eddi/peek) never reliably beats it. Fully **removing TSH** (`--drop-tsh`) just
shifts dominance to the next lab (FTI/TT4): fixed-best@3 = 0.692 ≈ full = 0.685; still no adaptivity.
**Cause: thyroid status is essentially ONE axis (hypo↔euthyroid↔hyper) that any single good lab
measures → one test suffices for everyone; multi-class did not create instance-specific test needs.**

**Meta-conclusion (PhysioNet + Diabetes-130 + Thyroid all FAIL the acquisition gate).** Adaptive-beats-
fixed requires **instance-specific best-features** (heterogeneous relevance). Real **single-target**
tabular data almost always has **global** feature relevance — one test/panel is best for nearly
everyone — so a FIXED panel is optimal and adaptivity has no room (this is why "greedy ≈ optimal" is
the standard budgeted-learning result). The missing ingredient is **multi-dimensional conditional
structure**: different instances genuinely need *different* expensive tests (differential diagnosis
across many diseases with disease-specific decisive tests). Multi-class over ONE axis (thyroid) does
not supply it, and such datasets are scarce / mostly credentialed. **Imposing tiered pricing cannot
manufacture heterogeneity the data lacks** — the acquisition-spread branch on real tabular data is
looking structurally hard, not just unlucky.

## 17. The positive spec — what an acquisition-band dataset MUST have
Turning three failures into a checklist. For an **acquisition** band (adaptive beats fixed), a dataset
needs **heterogeneous feature relevance**: *the decisive expensive feature varies per instance*, and a
cheap feature hints which one. Concretely, all of:

1. **Many acquirable expensive features** across cost tiers (not 5 labs on one axis) — so allocation
   has combinatorial room.
2. **Multi-dimensional discriminative structure**, NOT one axis. The canonical shape is
   **differential diagnosis / many-way classification where each class lives in a *different* feature
   subspace** — class A is decided by feature X, class B by feature Y. (Thyroid failed here: 3 classes,
   ONE axis, any lab suffices.)
3. **High signal** so the expensive features genuinely move the score (binding). (Diabetes-130 failed
   here: labs worthless for readmission.)
4. **A cheap "situation" signal** that narrows *which* expensive feature is decisive (the gate). If the
   cheap features carry no routing information, adaptivity can't beat random.
5. **The target is the thing the expensive features diagnose** — not a downstream outcome (§16).

Falsification is unchanged: the acquisition-spread gate (adaptive vs fixed vs random) — if a fixed
panel ties adaptive, one of 1–4 is missing.

**Where this structure lives (non-medical).** "Differential diagnosis" is not a medical-only shape —
any domain with *many outcome types, each identified by different signals, with cheap-vs-expensive
probes* qualifies. Strongest non-medical homes: **fault diagnosis / predictive maintenance** (many
fault types, each from different sensors), **network-intrusion / malware family classification** (many
attack/family types, each with different signatures; cheap flow stats vs expensive deep inspection),
**astronomical transient classification with follow-up** (this is *literally* an active-acquisition
problem — which follow-up observation to buy for which candidate type). These have MANY features and
genuine multi-dimensional structure, unlike the single-axis medical panels. Candidates enumerated and
screened per the gate (see the running notes / chat brainstorm).

**Dermatology RESULT — first PASS (proof-of-concept only).** UCI Dermatology (6 skin diseases, 11
free clinical + 22 expensive histopathology features) is the first dataset where **adaptive beats
fixed**: at B=6, eddi/peek-adaptive bAcc ≈ 0.90 vs **fixed-best plateaued at 0.844** — and fixed-best
*cannot* exceed 0.844 at any budget (a single fixed histopath panel can't serve all 6 diseases), while
adaptive reaches the full-panel ceiling (0.907) with just 6 of 22 features. That plateau-vs-ceiling gap
is the heterogeneous-relevance signature. The differential-diagnosis hypothesis (§17.2) is validated.

## 18. Resolution — a new criterion the Dermatology PASS exposed
A band you can't *measure* is useless. **Resolution** = achievable-score-range ÷ grading noise floor =
how many distinguishable score levels the test set supports. It is capped by the **rarest class**, not
total rows (balanced/macro metrics average per-class recalls; a k-instance class has recall SE
≈ √(p(1−p)/k)).

- Dermatology: test n=150, rarest class **7** → balanced-acc SE ≈ **0.035**, 95% CI ≈ ±0.07. Range
  random→full ≈ 0.124 → **only ~2 distinguishable levels**; the observed adaptive−fixed gap (0.037–
  0.060) is just **1–2 SE**, at the noise floor.
- **Can't be fixed by CV:** pooling all 366 rows still leaves the rarest class at ~20 → SE floor
  ≈ 0.021 → **~3 levels at absolute best.** Structurally too coarse.
- **Conclusion:** Dermatology proves the *structure* works but **can never be the buildable task** — a
  band needs many resolvable levels. Require a structurally-similar dataset **10–100× bigger with
  populous classes** (intrusion / fault-diagnosis, thousands–100k rows).

**Resolution as a pre-check (add to §5-style falsifiers):** before building, confirm the test set +
rarest class give a noise floor (≈2·SE of the metric) **well below** the achievable score range —
else even a real band collapses into 2–3 indistinguishable levels. *Want:* high. *Pre-checkable:* yes.

## 19. Non-medical sweep — and TEP PASSES the acquisition gate at scale
We ran the acquisition-spread gate on three non-medical candidates (#1 UNSW-NB15, #6 hydraulic, #8
Tennessee Eastman). Balanced-accuracy, deployable label-free buyers:

| Dataset | classes | free | full | fixed-best | eddi-adap | peek-adap | verdict |
|---|---|---|---|---|---|---|---|
| **#1 UNSW-NB15** (attack) | 6 | 0.58 | 0.80 | **0.79** | 0.79 | 0.79 | **FAIL** — fixed ≈ full (common feature set serves all attacks) |
| **#6 Hydraulic** (pump) | 3 | 0.33 | 0.997 | **0.997**@B5 | 0.99 | 0.99 | **FAIL** — cost-5 fixed panel = full; budget barely binds |
| **#6 Hydraulic** (valve) | 4 | 0.25 | 0.985 | **0.95**@B5 | 0.97 | 0.96 | **FAIL** — same |
| **#8 TEP** (fault, all 52 acquirable) | 22 | 0.045 | 0.897 | 0.792@B30 | 0.811 | **0.844** | **PASS** — fixed plateaus below full; adaptive climbs |

TEP detail (SE~0.048, ~4 resolvable levels): @B6 **peek 0.714 vs fixed 0.561** (+0.15 ≫2·SE); @B30
fixed-best 0.792 < full 0.897 while adaptive 0.811–0.844. The **dermatology plateau-vs-ceiling
signature at 22 classes** — a fixed panel can't cover all 22 faults, per-instance buying can.

**What this settles (corrects §16's pessimism).** Static tabular acquisition is **not** a dead zone.
The axis is **heterogeneity**, not tabular-vs-perceptual: *many classes, each perturbing/needing
different features, so no fixed panel serves all* → adaptive beats fixed. TEP (22 faults × 52 vars)
has it; the FAILS (PhysioNet/Diabetes/Thyroid/UNSW/Hydraulic) were single-axis or common-feature-set.
And the **peek ≫ eddi** gap is *real algorithmic headroom* — deployable policies capture only part of
the achievable band → **that gap is where students would spread.** The proposal's "planner beats
greedy" is achievable after all, given high-heterogeneity data.

**Two caveats keep TEP a SCAFFOLD, not the final task:** (1) TEP is a **simulation** → violates the
real-data rule; (2) it is a **well-known public benchmark** → memorization/hardcoding hack risk (must
anonymize features + relabel classes before any student eval). Use TEP to **validate the world
pipeline** (prompt, budget-enforcing grader, encapsulation, real student spread); the durable target
remains a **real, big, many-class differential dataset** (real fault-diagnosis / multi-condition).

## 20. What we built — the mediated-acquisition world (current state)
We stopped screening and BUILT the world on the TEP scaffold. The built system lives in
`worlds/budgeted/` + task `budgeted-tep` (mirrors the `multimodal_fusion` world; see `CLAUDE.md`).

- **Task shape.** The student (an LLM coding agent) ships a `Policy` class in `solution.py`:
  `__init__(data_dir)` trains on fully-observed train/val; `select_next(observed, budget_left) ->
  feat_id | None` and `predict(observed) -> int`. There is no `predictions.npy` — the grader DRIVES
  the policy. Budget binds only at test; sequential reveal is what lets adaptivity beat a fixed panel.
- **Mediated grader (the novel piece vs fusion).** At grade time `verify.py` spawns the policy as a
  subprocess dropped to the `model` user (sandboxed, no `/data_root`) and per test row runs the
  select→reveal→predict loop, ENFORCING the per-row budget and revealing only requested feature
  values. Test features + labels stay grader-only; labels are never transmitted. Metric = balanced
  accuracy; `best_observed = 1` (§9b).
- **Prompt.** Pure production framing (a classifier deployed under a per-case acquisition budget), with
  **no grading/eval/test-harness language** — the student is never told it is being graded.
- **Data.** Anonymized TEP (features shuffled + renamed `f0..f51`, classes relabeled) so the known
  benchmark can't be memorized. 52 features (analyzers cost 3, rest 1), per-case budget 15, 22 classes.
- **Anti-hack.** Budget enforced grader-side; `predict` only ever sees acquired features; labels in
  `/data_root` (700); student code sandboxed; anonymization defeats memorization.
- **Validated.** The mediated protocol was de-risked offline (oracle bAcc ~0.73 ≫ noop 0.045; budget +
  label-privacy asserted). The world builds hosted; the oracle Policy is masking-XGBoost + eddi
  acquisition. First hosted build tripped one bug (the artifact gate imported the student Policy in the
  grader venv, which lacks xgboost) — fixed by an AST-only structural check; the Policy's real behavior
  runs sandboxed.

**Status:** 7 hosted student runs launched (eval `2eb7b2e7-c573-40dc-b134-35776173f74d`) to measure the
actual spread — the first real test of whether students land at *different* scores (the band chased
since §1). **TEP stays a scaffold**; the durable target is a real, big, many-class differential dataset
(§17, §19) once the pipeline is proven here.
