# IPL Intelligence 360° — V2-J Offline QA Audit

**Result:** 34/34 checks passed; 0 failed.
**Browser acceptance:** Pending; cannot be inferred from this audit.

## Integrity and safety tests

- PASS — Master source/model unchanged: data/source/ipl_json.zip
- PASS — Master source/model unchanged: data/analytics/matches_enriched.csv
- PASS — Master source/model unchanged: data/analytics/team_match_summary.csv
- PASS — Master source/model unchanged: data/analytics/team_phase_match.csv
- PASS — Master source/model unchanged: data/analytics/player_registry_v2f.csv
- PASS — Master source/model unchanged: model_reports/model_gate_summary.csv
- PASS — Master source/model unchanged: model_reports/model_gate_report.json
- PASS — Master source/model unchanged: model_reports/qualified_model_names.json
- PASS — Master source/model unchanged: models_portable/chase_after_60_balls.json
- PASS — Master source/model unchanged: models_portable/chase_after_90_balls.json
- PASS — Master source/model unchanged: models_portable/chase_after_108_balls.json
- PASS — Master source/model unchanged: models_portable/first_innings_180_after_60_balls.json
- PASS — Master source/model unchanged: model_reports/holdout_predictions/chase_after_108_balls.csv.gz
- PASS — Master source/model unchanged: model_reports/holdout_predictions/chase_after_60_balls.csv.gz
- PASS — Master source/model unchanged: model_reports/holdout_predictions/chase_after_90_balls.csv.gz
- PASS — Master source/model unchanged: model_reports/holdout_predictions/first_innings_180_after_60_balls.csv.gz
- PASS — Research evidence is present
- PASS — Independent train/calibration/test match partitions reported
- PASS — User notebook in-sample predictions are not presented as qualified
- PASS — Corrected research all-state accuracy documented
- PASS — Retrospective after_10_overs cohort exists
- PASS — Retrospective after_15_overs cohort exists
- PASS — Retrospective after_18_overs cohort exists
- PASS — Only the original four checkpoint models are qualified
- PASS — Every qualified model is marked research candidate
- PASS — AI Prediction Centre has clearly separated live research tab
- PASS — Research chart uses descriptive title and shared full-screen viewer
- PASS — Capstone research guide links earlier live audit
- PASS — Ten dedicated franchise routes still exist
- PASS — Original credential-bearing Jupyter notebook not packaged
- PASS — Simulated franchise revenue CSV not packaged
- PASS — Previously uploaded in-sample live CSV not packaged
- PASS — No obvious hardcoded application credential assignments
- PASS — All existing academic deliverables preserved

## Scientific interpretation

The uploaded notebook generated in-sample model probabilities. This release keeps those outputs out of the four model deployment candidates. The separate rebuilt live model is a retrospective research baseline and **not an independently blind future-season result**.

## Nonautomatable acceptance

On Windows: actual Streamlit browser navigation, layout responsiveness, remote official CSK/team logos, animations, chart full-screen dialogs, upload/download interactions and chart legibility still need human verification.

## Source provenance

- Master immutable sources/models are tracked by SHA-256 in `V2J_Baseline_File_Hashes.json`.
- The original notebook may contain SQL credentials and is deliberately excluded.
- The simulated revenue CSV was not merged as factual historical finance data.
