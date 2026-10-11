# V3-D — research and sports-history release audit

## Module decisions

**Keep** existing four published checkpoint models. **Research only** the new team+opponent+venue model. **Integrate** sourced CLT20 and coaches without adding unverifiable historic coaching years. **Exclude** limited GitHub sentiment commentary datasets.

## Matched retrospective test: 2025–2026

|  | After 10 overs | After 15 overs | After 18 overs |
| --- | ---: | ---: | ---: |
| Match-level samples | 138 | 132 | 100 |
| Existing model accuracy | 81.16% | 89.39% | 90.00% |
| Context research model accuracy | 77.54% | 88.64% | 88.00% |
| Existing Brier | .13608 | .08746 | .06850 |
| Context Brier | .14250 | .10017 | .07580 |

Context models are fitted on 2008–2024 after an earlier 2008–2022 development split and no tuning on test seasons. Existing portable checkpoint models are evaluated on the **same match IDs**. Existing baseline training pipeline is not identical to the context pipeline, so this is a candidate-vs-incumbent comparison rather than a clean randomized feature ablation. Predictions for the 2025–2026 cohorts had already been examined in the broader project; do not call them fresh prospective holdouts.

This model does **not** infer a player-aware forecast. UI player names are context for human interpretation only. Historical Cricsheet lineups may include Impact Players, and player observations require point-in-time discipline. Player portrait and authenticated match availability would require more verified data.

### Selection principles

The project has a 70% minimum meaningful-accuracy policy for deployed classification models, but that number is necessary, not sufficient. The new model clears 70% yet **does not beat the existing baseline** and has worse proper probability scoring. It is therefore explicitly **not deployed as a qualified winner predictor**.

### Coaching validation

Official 2026 head-coach snapshots: 10 of 10 IPL franchises; historical tenure statistics only CSK and MI (the sources explicitly cover them). Coaching-era win rates use actual IPL team-match summary records; only decided matches enter the win-rate denominator. Historical coaching eras do not imply coach-specific causal impact. CSK's coach Stephen Fleming departed after the IPL 2026 season, so the 2026 entry is labeled by *season*, not as a current appointment.

### CLT20 validation

The entire six-edition historical roll (2009–2014) is sourced; two titles for CSK (2010, 2014), two for MI (2011, 2013). Club records and domestic IPL trophy totals are kept separate; non-IPL teams New South Wales Blues and Sydney Sixers are preserved rather than assigned IPL franchise IDs.

### Sources

- BBC: https://www.bbc.co.uk/sport/cricket/29493937
- Mumbai Indians history: https://www.mumbaiindians.com/history
- Mumbai Indians coach eras: https://www.mumbaiindians.com/amp/news/teachers-day-special-remembering-all-our-mi-head-coaches-on-their-special-day
- CSK coaching transition: https://www.reuters.com/sports/cricket/fleming-steps-down-chennai-head-coach-after-18-years-charge-2026-07-13/
- IPL 2026 official team profiles: URLs in `data/metadata/coaches_2026_source_snapshots.csv`
- Ground truth IPL matches/deliveries: original supplied Cricsheet dataset inside `data/source/ipl_json.zip`.

## Remaining gaps

Actual interactive Streamlit browser acceptance remains pending. Some 2026 coach pages on official IPL may later be updated; keep historical snapshots rather than treating pages as stable archival evidence. Additional coach era datasets are needed for KKR, RCB, RR, SRH, DC, PBKS, GT and LSG. No first-class player availability, pitch, weather, or match-specific lineup verification is present in the new research model.
