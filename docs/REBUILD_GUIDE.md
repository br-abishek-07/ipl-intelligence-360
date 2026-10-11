# IPL Intelligence 360° V4Z — End-to-End Rebuild & Technical Documentation

**Release:** V4Z Fact-Checked Fan Wars / curated franchise edition.  
**Application:** Python 3.12, Streamlit, pandas, NumPy, Plotly, ReportLab.  
**Last historical season represented:** IPL 2026.  
**Reproduction contract:** This guide explains how to reproduce the *published V4Z runtime from packaged tables and portable models* and how to recreate the upstream analytical methodology. The public runtime package does not contain every notebook or historical training script from earlier phases. Exact model retraining from raw JSON is therefore **not** guaranteed without retrieving those earlier source scripts, feature specs, random seeds and splits.

## 1. Problem, users, outputs

The project answers four questions.

1. **What happened?** League season trends, score progression, player runs and wickets, team achievements, rivalries, venue and phase metrics.
2. **What patterns matter?** Team-specific KPIs and DNA across powerplay, middle overs, death overs, chasing, bowling, and historical comparisons.
3. **What may happen?** Four historical match-state classification models and independently labeled, experimental franchise-decision models.
4. **How can fans and analysts test opinions?** An interactive collection of 19 controversial IPL claims, with their actual counts, definitions, source and limitations.

The intended audience is students, fans and analysts. It is *not* a real-time licensed scoring feed, official roster service or causal team-selection optimizer.

## 2. Input data and provenance

**Primary:** Cricsheet IPL ball-by-ball JSON archive, 1,243 matches from 2008–2026, containing 295,732 recorded delivery objects. The app's audit reports 295,557 regulation delivery objects after separating Super Overs, plus 27,909 participant/lineup entries. File supplied in the deployment package: data/source/ipl_json.zip.

**Normalized historical tables:** data/raw/matches.csv.gz, data/raw/deliveries.csv.gz, data/raw/lineups.csv.gz and data/raw/wickets.csv.gz; analytics tables are in data/analytics/. For historical 2026 squads, source-dated snapshots are in data/metadata/.

**Additional metadata:** historical IPL final captains with sourced registry, coaching-era registry with documented gaps, 2009–2014 CLT20 roll of honour, match stage and venue alias mappings; player-of-match awards. This material is intentionally distinct from playing-XI observations and match outcomes.

**Auction:** data/raw/auction_sales.csv contains selected historical sales, **not** a comprehensive ledger of sold, unsold, withdrew and passed-over nominees. Never infer a sold/unsold target from missing rows.

**Cross-league:** the V4X research tables in data/v4x/ include precomputed SMAT/BBL scouting features; their completeness and competitive-strength comparability are limited. The cloud bundle is optimized for *inference*, not for repeating raw cross-league ingestion.

**Provenance:** retain original source URLs, snapshot dates, row counts and file checksums. Consult reports/data_quality_audit.json, reports/eda_findings.md, reports/v4x/V4X_Independent_Model_Audit.md, and the V3 coaching/finals audits. Check Cricsheet and third-party redistribution terms before publishing original records.

## 3. Obtain source and install runtime

Clone the repository **after all public-ready files have been uploaded**, or extract the V4Z public-ready ZIP directly into a new directory. At the root you should see:

~~~
app.py
requirements.txt
.python-version
.streamlit/config.toml
preflight_public.py
dashboard/
pages/
data/
models_portable/
model_reports/
reports/
assets/
docs/
~~~

On Windows PowerShell:

~~~powershell
cd path\to\ipl-intelligence-360
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python preflight_public.py
python -m streamlit run app.py
~~~

If PowerShell activation is blocked, use .\.venv\Scripts\python.exe instead of the generic python command. Other systems: create an equivalent Python 3.12 virtual environment. Default URL is http://localhost:8501.

**Runtime requirements:** streamlit>=1.39,<2; pandas>=2.1,<3; numpy>=1.26,<3; plotly>=5.22,<7; reportlab>=4.2,<5. Production inference uses portable JSON, so scikit-learn and joblib aren't required to *run* the four deployed models.

## 4. Rebuilding from raw cricket JSON: documented transformation design

To reconstruct the analytical warehouse from its sources:

1. **Extract and validate JSON.** Iterate Cricsheet match files. Store immutable original match identifier and source archive hash. Parse metadata (date, season, venue, teams, toss, outcome, match type), innings and delivery objects. Reject malformed source schema and record missing observations explicitly.
2. **Create identity registry.** Use stable Cricsheet player IDs and aliases from people/name registries. Do not merge two players on fuzzy spelling alone. Preserve historical franchise name changes separately from discontinued franchise identities.
3. **Flatten deliveries.** Emit one record per recorded delivery object, with match ID, innings, batting/bowling sides, striker/bowler IDs, over number, within-over index, batter runs, extras by subtype, total runs, wickets and legal-ball indicator.
4. **Handle cricket laws.** Wides and no-balls are not legal deliveries; byes and leg byes may still be on legal balls. Keep total runs and batter runs distinct. Credited bowler wickets exclude run-outs and relevant non-bowler dismissals. Keep Super Over deliveries flagged instead of adding them to 20-over innings.
5. **Match result reconciliation.** Use regulation match result and explicit Super Over eliminator winner where supplied; unresolved or no-result matches must not be forced to wins/losses. Keep DLS/reduced matches flagged for appropriate exclusions.
6. **Venue and team normalization.** Maintain raw stadium strings and a documented mapping, including uncertainty. Older Delhi Daredevils and Kings XI Punjab are historically mapped to DC/PBKS for continuity, without silently treating Deccan Chargers as Sunrisers Hyderabad.
7. **Derive grain-safe tables.** Maintain independent tables at match, match-by-team, innings, match-by-player batting, match-by-player bowling, team-by-phase-by-match, player-by-phase-by-match and season grains. Document primary keys and confirm there are exactly two current teams per standard match.
8. **Build metrics.** Batting SR = 100*batter runs / legal balls faced, with cricket-specific exclusions; bowling economy = total chargeable runs*6/legal balls bowled; boundary rates and phase rates use documented denominators. Win percentage = resolved wins / resolved games, excluding non-decisions. Never compare metrics without displaying sample sizes.
9. **QA reconciliation.** Check unique match IDs, source-to-flat delivery totals, run conservation (bat + extras), wickets, innings total reconstruction, team-match row counts, orphan player/match references, and exceptions for ties, reduced innings and Impact Players.
10. **Store partitionable outputs.** Save the normalized CSV/GZIP files under data/raw/ and data/analytics/, and a machine-readable audit JSON under reports/.

**Important:** Steps 1–10 describe the original project's pipeline approach, not a claim that this public ZIP includes a turnkey reconstruction script. For exact byte-for-byte rebuilding, retrieve the original Phase 1/Phase 2 ETL implementation or reproduce the schema/rounding decisions and compare the result to the bundled data.

### Required analytical tables and their use

| File | Grain | Purpose |
|---|---|---|
| data/analytics/matches_enriched.csv | match | filters, match winner, dates, venue, toss and stage |
| data/analytics/team_match_summary.csv | match × franchise | match results, franchise KPIs, head-to-head |
| data/analytics/innings_summary.csv | match × innings | totals, targets, scoring trends |
| data/analytics/league_season_summary.csv | IPL season | season EDA |
| data/analytics/team_phase_match.csv | match × team × innings phase | Team DNA batting/bowling rates |
| data/analytics/batting_player_match.csv | match × batter | runs, balls, fours, sixes, strike rate |
| data/analytics/bowling_player_match.csv | match × bowler | overs, chargeable runs and credited wickets |
| data/analytics/player_registry_v2f.csv | player ID | searchable names and aliases |
| data/analytics/player_of_match_awards.csv | awarded match | performance recognition |
| data/metadata/ipl_2026_post_auction_squads_sourced.csv | dated squad member | reported 2026 squad **snapshot**, not current roster |

## 5. Streamlit application architecture

The entry point **app.py** configures the page and group navigation with st.navigation and st.Page. It intentionally curates the main sidebar while retaining older research source modules. The user-facing navigation groups are:

- **League & Franchise Intelligence:** IPL League Explorer, Franchise Comparison, CSK, MI, RCB, KKR, SRH, RR, DC, PBKS, GT and LSG pages.
- **Player & Match Analysis:** Player Intelligence, Team DNA & Strategy, Records & Legends, sourced Finals Captaincy, Match Replay & Rivalry, Coaches & CLT20, Sports Analyst Report Studio and IPL Fan Wars.
- **Predictions:** Chase & Score Predictions.
- **Research (optional):** Research, Model Tests & Capstone. Metrics are intentionally absent from everyday cricket dashboards.

Key modules:

| Module | Function |
|---|---|
| dashboard/data.py | Root-relative data paths and reusable table loading |
| dashboard/views.py | Home, team desks and league views |
| dashboard/analytics.py and franchise_analytics.py | Descriptive sports metrics |
| dashboard/design.py and chart_ui.py | Dark/team-themed cards and consistent fullscreen-capable Plotly rendering |
| dashboard/player_page.py and player_intelligence.py | Name search and player histories |
| dashboard/team_dna.py and team_dna_page.py | Relative team dimensions, phase and peer comparisons |
| dashboard/v3_match_engine.py and v3_match_page.py | Ball replay, wicket/over trajectories, head-to-head |
| dashboard/squad_2026.py | Sourced roster vs *observed* match participants |
| dashboard/analyst_reports.py and report_studio_page.py | Generate evidence-linked PDF and structured CSV exports |
| dashboard/debates_page.py | Controversial-question interface |
| dashboard/predict.py and prediction_lab_v2.py | Portable match-state predictions and scenario input validation |
| dashboard/research_vault.py and franchise_decision_lab.py | Model evaluations, experimental research and limitations |

The single dashboard source of truth for selected filters is the relevant filtered match subset. All derived KPIs and exported tables must use consistent match IDs and denominators. Controls should have unique Streamlit keys; charts must use dashboard/chart_ui.py for descriptive names and full-screen viewing. Cache heavyweight immutable data loading with st.cache_data, while avoiding stale variable-specific caches.

## 6. Four deployed match-state prediction models

The JSON model files are:

1. models_portable/chase_after_60_balls.json — second-innings win probability at the 10-over chase checkpoint.
2. models_portable/chase_after_90_balls.json — second-innings win probability at 15 overs.
3. models_portable/chase_after_108_balls.json — second-innings win probability at 18 overs.
4. models_portable/first_innings_180_after_60_balls.json — probability the first innings exceeds the 180-run threshold after 10 overs.

dashboard/predict.py constructs numeric features from the user-entered score, target, wickets, overs/balls and applicable match state. Portable JSON inference avoids pickling/version dependency. Inspect model_reports/model_gate_report.json and model_gate_summary.csv for the saved results and threshold criteria; never substitute a narrative number for the actual report.

### Correct experimental evaluation, if retraining

- Define **prediction time** explicitly: the chosen checkpoint and information available at or before it.
- Split by **match**, preferably chronologically by **season**, so no delivery states from the same match straddle train/test.
- Train only using seasons earlier than the validation/test period; recompute feature priors *as of the prediction date*.
- Evaluate accuracy and balanced accuracy relative to naive baselines; ROC-AUC and Brier score/calibration for probabilities; class prevalence and sample size.
- Use per-match or match-clustered bootstrapping, not naive confidence intervals over highly correlated deliveries.
- Freeze features and model selection before final holdout; because IPL 2025/26 were used during iterative development, treat those results as **retrospective**, not a future prospective test.
- Flag DLS, revised targets, super overs and abandoned matches, and never let end-of-match outcomes enter point-in-time inputs.

The public bundle retains trained inference JSON and audit tables but may not include the exact training feature pipeline and historical model-selection notebooks. Consequently, it reproduces *saved predictions*, not automatically all training decisions.

## 7. New franchise research (not deployed as superior recommendations)

The V4X research data was built using historical information through 2023, validation in 2024, and retrospective 2025–2026 tests.

| Task | 2024 | 2025 | 2026 | Decision |
|---|---:|---:|---:|---|
| Powerplay bowler deployment | 82.04% acc | 81.80% | 81.39% | promising phase-use classification, not optimal bowling advice |
| Death-overs bowler deployment | 79.19% acc | 75.02% | 73.99% | promising phase-use classification |
| Match participation | 84.59% acc | 84.26% | 82.76% | little improvement over repeat-last lineup; research only |
| Batter runs per recorded delivery | 1.323 MAE | 1.343 | 1.390 | trails naive mean baseline in 2026 |
| Next-season IPL batter SR | 23.770 MAE | 25.280 | 24.611 | conditional selection and negative R²; research only |

The two phase-use classifications are about *whether a given prior-candidate bowler is deployed*, NOT whether that selection improves expected runs saved. The match-participation label may include Impact Players and does not mean starting XI. The auction file does not supply reliable unsold labels, so no trained auction sold/unsold predictor or fair-value model is claimed. See reports/v4x/V4X_Independent_Model_Audit.md.

## 8. Debate Lab and evidence policy

The Fan Wars interface (pages/26_Cricket_Debate_Lab.py and dashboard/debates_page.py) loads **19 precomputed questions** in reports/v4y/RAGE_BAIT_IPL_DEBATES_VERIFIED.json and CSV/Markdown counterparts. Each record has: number, category, question, answer, evidence, interpretation_limit, data_source, scope, confidence and metric labels/values. These reflect the provided 2008–2026 data snapshot.

Examples:

- Toss winners won 634 of 1,234 *decided* matches: **51.38%**, not proof toss advantage has no contextual effect.
- The chasing team won 672 of 1,234 decided matches: **54.46%**, not a recommendation to chase every target.
- First-innings scores >=200 were defended in 162 of 213 eligible matches; 51 were lost. The precise denominator/exclusion criteria matter.
- CSK–MI head-to-head is 20–21 in 41 decided meetings; this is a narrow rivalry, not comprehensive proof of greatness.
- Comparing Kohli/Rohit batting runs does not resolve captaincy or team-trophy superiority.

**Do not label the posts "most frequent on Reddit/Quora" based on an unsystematic search.** These are curated controversy *themes*, not a statistically representative fan opinion sample. Quora may restrict automated access. Scores and illustrations should be separated: generated promotional infographic images may contain typographic mistakes and must not be the final numerical evidence source.

## 9. 2026 roster, captaincy and CLT20 cautions

- dashboard/squad_2026.py displays a 25-player-per-team *post-auction snapshot dated December 16, 2025* for all ten current teams. It separately displays players who appear in 2026 Cricsheet match participant lists. The latter can include Impact Players and is not an authenticated XI or continuously updated contract registry.
- The 2026 retention source is data/metadata/ipl_2026_official_retention_source_2025_11_15.json. As-of date, trades and replacement entries matter.
- The captaincy registry covers **finals only** (38 captains in 19 finals), not every captain's season-by-season record; do not invent overall captain win percentage.
- Coaching-era metadata only covers verified periods and intentionally preserves missing seasons.
- CLT20 2009–2014 history stays **separate** from IPL trophy totals.

## 10. Quality gates before calling this professional

Run:

~~~powershell
python preflight_public.py
python -m streamlit run app.py
~~~

Check that:
1. Home and League Explorer load and display match/season totals.
2. All **ten franchise pages** load, and filters change a KPI and at least two independent visuals.
3. The 2026 snapshot and recorded participants are correctly distinguished.
4. Player search resolves Cricsheet display aliases (e.g., KD Karthik, V Kohli).
5. Match replay excludes Super Overs from ordinary innings until explicitly selected.
6. Team DNA single-season/range controls update the selected team and comparable peer populations.
7. Chase/score input validation prevents nonsensical states and models remain available.
8. The PDF report exports successfully; source and match filters remain visible.
9. Fan Wars shows the full 19-record library and underlying evidence/limitations.
10. The Research page contains evaluation but the front page does not sensationalize model accuracy.
11. Chart expand/full-screen interaction, remote team marks and mobile width are checked *in a browser*.
12. In the public URL, incognito access works and no secrets/absolute local paths leak into logs.

The public package is syntax/preflight checked but no claim of complete Windows or deployed-browser acceptance can be made until a human verifies it.

## 11. Deployment and repeatability

Public hosting: GitHub repository + Streamlit Community Cloud. Settings: repository main branch, main file **app.py**, Python **3.12**, root requirements.txt. Never commit .env, secrets.toml or credentials. See docs/DEPLOYMENT.md.

For future research, freeze and tag dataset SHA-256 and training cutoff date, store a feature dictionary, train/validation/test match IDs, random seed and evaluation JSON in version control, and only promote models that beat naive baselines with acceptable calibration on an untouched later season.

## 12. What must be sourced to recreate everything from first principles

The runtime package is sufficient to run the **saved V4Z experience** once all files have been added to the repository. To regenerate the processed warehouse and retrain models without referring to these outputs, an independent rebuilder additionally needs:

- Original Phase 1/2 cleaning + JSON-flattening scripts, fixed schema definitions and team/venue alias maps.
- Stable Cricsheet player-ID crosswalk and any approved auxiliary squad/coach/finals source snapshots.
- Full training/feature-engineering scripts for the four portable match-state models, with exact season splits, hyperparameters, label rules, and serialized model specs.
- Original raw SMAT and BBL archives and their feature builder for cross-league scouting research.
- A reliable auction sold/unsold outcome ledger if an auction classifier is attempted (not available in this V4Z build).
- Tests that compare regenerated outputs to packaged reference tables and check source licences.

**Academic wording:** "This repository includes a reproducible runnable dashboard with packaged derived tables and inference models. End-to-end *training-data regeneration and identical retraining* require the archived ETL and model-development pipeline." This distinction is fundamental to credibility.
