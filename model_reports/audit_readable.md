# Phase 3D — Automated Accuracy Gate Audit

Evaluation: trained through 2022 / model selection 2023–2024 / refit through 2024 / held-out seasons 2025–2026.
Holdout seasons were previously inspected in earlier phases. All approvals are **retrospective/provisional**.

## Qualifying models (4)
- chase_after_60_balls: accuracy=82.35%, 95% lower Wilson=75.08%, ROC-AUC=0.907, majority=57.35%, Brier=0.134, n=136, 2025=82.09%, 2026=82.61%
- chase_after_90_balls: accuracy=90.00%, 95% lower Wilson=83.64%, ROC-AUC=0.954, majority=56.92%, Brier=0.086, n=130, 2025=86.15%, 2026=93.85%
- chase_after_108_balls: accuracy=90.82%, 95% lower Wilson=83.46%, ROC-AUC=0.975, majority=50.00%, Brier=0.064, n=98, 2025=89.58%, 2026=92.00%
- first_innings_180_after_60_balls: accuracy=82.07%, 95% lower Wilson=75.02%, ROC-AUC=0.882, majority=66.21%, Brier=0.128, n=145, 2025=79.45%, 2026=84.72%

## Rejected model candidates (8)
- chase_after_0_balls: accuracy=65.22%, reason=Accuracy below 70%
- chase_after_36_balls: accuracy=76.81%, reason=95% Wilson accuracy lower bound does not exceed 70%
- first_innings_180_after_36_balls: accuracy=71.03%, reason=95% Wilson accuracy lower bound does not exceed 70%
- first_innings_180_after_90_balls: accuracy=87.79%, reason=Does not beat naive current-run-rate extrapolation by >1pp
- bat_30_plus_if_bats: accuracy=69.68%, reason=Accuracy below 70%
- bat_50_plus_if_bats: accuracy=85.66%, reason=Less than 3 percentage points above cohort majority baseline
- bowl_1_plus_if_bowls: accuracy=62.37%, reason=Accuracy below 70%
- bowl_2_plus_if_bowls: accuracy=74.27%, reason=Less than 3 percentage points above cohort majority baseline

## Safeguards

- Fixed test checkpoints / one row per match; no post-ball predictor columns.
- Train/validation/test split by season; no random-ball split.
- Chase matches have winner and regular 20-over target; D/L and reduced overs excluded.
- Player-history covariates shifted to past matches.
- Rejected models not stored in approved `models/`.
- Missing prior-season player stats imputed by fitted training pipeline.
- No external data scraped and no original Cricsheet records modified.
- All tested task accuracies refer to their EXACT outcome definitions.
