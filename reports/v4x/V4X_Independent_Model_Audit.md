# IPL Intelligence 360° — V4X: Franchise Decision Intelligence

## Executive summary

This upgrade implements four *research-model families*, with portable JSON inference in a **new page inside the V4 capstone**. It does not replace the four original IPL match-state prediction models.

Data train: historical seasons **through 2023**. Independent training exclusions: **2024 validation**, **2025 retrospective test**, **2026 retrospective test**. In live terms these seasons are not a genuinely pristine test set, because 2025/26 had already been examined in earlier model development. Predictions are computed using match- or season-previous information, not same-fixture results.

## Full evaluation in concise form

| Task | 2024 validation | 2025 test | 2026 test | Required naive comparison | Practical decision |
|---|---:|---:|---:|---|---|
| Bowling role — powerplay | 82.04% | 81.80% | 81.39% | 2026 repeat-last baseline 79.67% | Pilot research: beats naive baselines |
| Bowling role — death overs | 79.19% | 75.02% | 73.99% | 2026 repeat-last baseline 70.47% | Pilot research: beats naive baselines |
| Bowling role — both phases | 80.61% | 78.41% | 77.69% | 2026 repeat-last baseline 75.07% | Pilot research: beats naive baselines |
| Match participation, not actual starting XI | 84.59% | 84.26% | 82.76% | 2026 repeat-last baseline 82.64% | Research only; tiny lift not robust |
| Batter runs per delivery | 1.323 | 1.343 | 1.390 | 2026 baseline MAE 1.348 | Research only; fails MAE baseline |
| Next-season IPL batter strike rate | 23.770 | 25.280 | 24.611 | 2026 baseline MAE 25.944 | Research only; negative R² |

### Accuracy uncertainty: match-clustered paired bootstrap

To account for multiple correlated player/phase rows in one game, sampled each complete match with replacement 2,000 times. Effect = AI accuracy minus repeating the previous match's phase selection, on the identical rows. Confidence intervals reflect match-to-match sampling uncertainty, *not* dataset shift or future model reliability.

- **bowling_overall:** n=5,586 eligible cases, 148 matches, model 78.05% vs last-match 75.67%; lift **+2.38 pp**, 95% interval **[+1.24, +3.52] pp**.
- **bowling_powerplay:** n=2,793 eligible cases, 148 matches, model 81.60% vs last-match 79.91%; lift **+1.68 pp**, 95% interval **[+0.46, +2.96] pp**.
- **bowling_death:** n=2,793 eligible cases, 148 matches, model 74.51% vs last-match 71.43%; lift **+3.08 pp**, 95% interval **[+1.66, +4.51] pp**.
- **participation_overall:** n=4,852 eligible cases, 148 matches, model 83.51% vs last-match 83.37%; lift **+0.14 pp**, 95% interval **[-0.10, +0.47] pp**.

## What exactly was predicted?

1. **Bowling deployment** (binary): will this bowler appear during overs 1–6 or 16–20? Candidate pool consists of bowlers who played for this franchise in *preceding* team matches, NOT an authenticated roster for the upcoming match. Training examples have one player × phase × match; player/phase priors are built only from previously completed matches. Predicting actual selection is not optimizing which bowler should be used.
2. **Match participation** (binary): will a previously involved player appear in the next recorded match participant list? Recorded participation can include Impact Player substitutes; this **is not** a starting-eleven classifier and does not predict debutants absent from the historical pool. Baseline repeat-last-participation is already high; incremental predictive benefit is negligible.
3. **Batter–bowler run risk** (regression): next recorded delivery's batter runs. Inputs include innings phase, batter/bowler prior completed-season scoring/boundary rates, and direct pre-season matchup history. It does **not** condition on current over momentum, the current state, bowlers' overs remaining, pitch, or injury. Performance currently trails a simple phase mean on MAE. Expected runs under different bowlers are **associations**, not proven causal runs-saved estimates.
4. **Cross-league scouting** (regression): batter's IPL season strike rate **conditional on at least 30 batting balls in the target season**. Uses prior IPL performance and separately tracked past SMAT/BBL statistics through seasons before the target year. It **does not** assess a player's likelihood of receiving batting opportunities or IPL selection; out-of-IPL samples are incomplete. Modest MAE reduction compared with prior IPL career SR does not offset poor negative R². This is research only.

## Auctions: a deliberately blocked claim

Existing historical auction file provides **969 valid sold-price records** from 2013–2022 but no complete unsold, called, withdrawal, or round-by-round auction outcome register. The current 2025/26 scraped auction pages are incomplete and mix retention contract amounts with auction results. **No auction sale probability or fair value predictor has been deployed.** The new page provides only descriptive historical sale-price analysis. Reliable models require verified outcomes, currency/crore normalization, dated rosters, and as-of rules.

## Data and provenance

- Cricsheet IPL archive: 1,243 matches, 295,732 delivery objects (regulation source retains some incomplete/abandoned matches). Original V4 data preserved unchanged.
- Syed Mushtaq Ali Trophy source: 695 JSON matches through 2024. Big Bash League source: 662 JSON matches through January 2026. Source archives are included under `research_v4x/` for model reproduction. Non-IPL evidence is kept separate by league.
- Player IDs are Cricsheet IDs. The Hundred uses a 100-ball format and was intentionally excluded from standard over-rate training. The user's T20 international audit describes additional data but no actual T20I ZIP is included in this build.
- All four trained research models are linear models stored as *portable JSON*. They require no sklearn installation for dashboard inference. Research retraining requires `requirements_research.txt`.
- No model was optimized to maximize performance on 2025/26; supervised fitting was frozen through the 2023 season.

## How to run

```powershell
py -m pip install -r requirements.txt
py -m streamlit run app.py
```

Then navigate to **Franchise Decision Intelligence Lab**. For a reproducible research run:

```powershell
py -m pip install -r requirements_research.txt
py research_v4x/train_all.py
py research_v4x/match_cluster_audit.py
py -m unittest discover -s research_v4x -p test_v4x.py -v
```

## Academic and governance limitations

- Per-player examples within a match are correlated; match-cluster confidence intervals are supplied.
- Model fit is a historical backtest, not independently certified future prospective performance.
- Effects are conditional on candidate pools generated from prior matches, not all actual players available to franchise management.
- For true Playing XI prediction we need *confirmed pre-toss team rosters* and separate starter/Impact labels.
- For decision optimization we need counterfactual action evaluation, opponent batting intent, injury/availability, and bowling allocation constraints.
- For authentic future-player forecasting we need age/availability/role and competition-adjusted scouting samples, plus exposure predictions.
- The old four checkpoint models remain the only existing user-facing qualified prediction models, unchanged. Bowling deployment is a **promising pilot**; it does not replace or certify production decisions.
