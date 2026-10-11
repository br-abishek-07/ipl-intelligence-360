# IPL Intelligence 360° — V2-G AI Prediction Centre: Research and QA

## Goal and scope
This is an **explanation and evaluation upgrade**, not a model retraining exercise. It integrates four portable JSON classifiers from Phase 3D into the single Streamlit app, with scenario comparison and sports-analyst notes. The original model features, coefficients/tree nodes, event definitions, evaluation populations and portable model files were retained unchanged.

## Four checkpoints and honest interpretation

| Model | Eligible input | Binary outcome | Previously reported retrospective holdout accuracy | Matches | Majority class |
|---|---|---|---:|---:|---:|
| Chase after 10 overs | Active, full-length chase after exactly 60 legal balls | Chasing team eventually wins | 82.35% | 136 | 57.35% |
| Chase after 15 overs | Active, full-length chase after exactly 90 legal balls | Chasing team eventually wins | 90.00% | 130 | 56.92% |
| Chase after 18 overs | Active, full-length chase after exactly 108 legal balls | Chasing team eventually wins | 90.82% | 98 | 50.00% |
| Innings 180+ after 10 overs | Active first innings, 60 legal balls, <180 runs | Final innings total reaches at least 180 | 82.07% | 145 | 66.21% |

The model-selection workflow used 2025–2026 results across iterations: therefore the 2025–2026 set is **retrospective** and no longer truly independent of the overall development process. An untouched future-season evaluation is necessary before any production-grade generalization claim. **Accuracy refers to each task's binary classification, not the individual displayed probability.**

### Eligibility and limitations
- Correct checkpoint only; 10/15/18 overs for chase, 10 overs first innings.
- Chases exclude rain-shortened matches, no-results and conditions outside a standard 20-over regulation innings. A finished chase or all-out side is not an eligible model state.
- Targets must be entered as **runs needed to win** (e.g. chasing 181 requires target=181). The simulator does not support independent tie/Super Over or DLS outcome probabilities.
- No team, venue, pitch, live player, current bowling resource, injuries or weather input. This is a **match-scoreboard model**, not a team-level or squad-aware prediction.
- Extreme hypothetical scoreboard combinations can be outside the distribution of training data.
- The simulator is manual; it does not ingest live scores, feeds or APIs.

### What-if and visual explanations
- Probability gauges show event probabilities, not confidence in the accuracy of that specific prediction.
- Sensitivity lines and wickets charts recompute the **same trained model** after changing runs or wickets. This is **counterfactual model response**, not feature importance, Shapley values, or a causal effect.
- Two-scenario comparison holds the target and checkpoint fixed, but when both runs and wickets change the resulting probability gap cannot attribute a cause to either.
- Sports analyst briefings explain current/required run rate and wicket resources using arithmetic. They do not infer a causal strategy.

### Genuine holdout evaluation
The original match-level evaluation CSVs were obtained from Phase 3D `outputs/*_holdout.csv` and copied into `model_reports/holdout_predictions` with only:
- match_id
- season_year
- observed_outcome
- probability

Each checkpoint has exactly one row per independent historical match. The source filenames and original model gate are retained. Reported accuracies, Brier scores, cohort sizes and majority baselines are recomputed from these rows and verified with automated tests. The confusion matrix is calculated at a user-chosen threshold, default 50%; threshold selection does not retrain models. Calibration uses five 20-percentage-point bins and is sparse for some models. The per-season plot uses 2025 and 2026 retrospective observations. The dashboard displays eight rejected candidates only in the methods/audit view, never for public prediction.

### Model interface contracts
`dashboard/predict.py` is unchanged from V2-F and handles portable JSON logistic regression and histogram gradient boosting. The exact feature builders (`chase_features`, `total_features`) are reused; no label leakage or new estimator claims. The Prediction Centre `dashboard/prediction_lab_v2.py` calls the established `dashboard/chart_ui.py` `render_chart` for **every new chart**. Keys are unique and titles describe the analytical question. Charts have full-screen and HTML export controls.

## Reproducibility and automation

```powershell
py -m pip install -r requirements.txt
py -m streamlit run app.py
```

QA (extra developer package required):

```powershell
py -m pip install -r requirements-dev.txt
py -m pytest -q
```

See the notebook `notebooks/V2G_AI_Model_Evaluation.ipynb`. Original Cricsheet files, Phase 2 source archive, all ten team dashboards, IPL league EDA, player lab and Records/Legends sections are preserved.

## External testing still needed
The build environment cannot run Streamlit in a real browser. On Windows, check all five tabs in AI Prediction Centre, mobile/desktop widths, full-screen chart overlay, the sliders, empty/invalid input states, and downloads. Full-page fake Streamlit execution does **not** guarantee pixel-perfect browser behavior.
