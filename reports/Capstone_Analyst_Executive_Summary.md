# IPL Intelligence 360° — Executive Research Summary
**AI-Driven Data Science Capstone | Sports Analyst Perspective**

## Decision problem
In cricket, a scoreboard reports **what happened**, but a performance analyst must identify **which patterns are reliable** and how to translate them into decisions. This application analyzes league-wide scoring, franchise results, venue associations, bowling and batting phases, historical player performance and selective evidence-based predictions.

## Data actually analyzed
- **1,243 IPL matches** from 2008–2026 and **295,557 regulation deliveries**, after excluding **175 Super Over event deliveries** from normal scoring aggregation.
- The Cricsheet original JSON is included **without modification**, along with compressed Phase 2 normalized tables for reproducibility.
- **16 tied matches** had a final Super Over winner in Cricsheet `outcome.eliminator`; **9 matches remain without a final winner**. The project counts final wins where justified and excludes unresolved games from win-rate denominators.
- **557 match/team player-list entries** contain a number other than 11 and are **not** interpreted as confirmed starting XIs.

## Five analytical findings worth presenting

### 1. First-innings scoring has risen in the eligible historical sample
The average among first innings with >=100 legal balls and without DLS was:
- **2022:** 173.6 runs from 72 qualifying innings;
- **2023:** 182.2 from 72;
- **2024:** 190.1 from 70;
- **2025:** 195.2 from 68;
- **2026:** 197.5 from 70.

**Sports interpretation:** More aggressive scoring and rule-era changes are candidate explanations, **not tested causal findings**. For tactical context, batting par scores should be estimated with the ground, phase, season and available squad, not using a single lifetime average.

### 2. Scoring rates vary sharply by phase
Across recorded regular innings, the IPL run rate was approximately **8.09** per six legal balls during powerplays, **7.95** during overs 7–15, and **10.06** during overs 16–20. These are legal-ball-weighted averages, not unweighted averages of inning rates.

**Sports interpretation:** A team's death-over hitting and its ability to limit conceded death-over runs are separate capabilities. The dashboard compares each franchise with the **same-season IPL benchmark** rather than a misleading league-wide average across eras.

### 3. Apparent franchise win-rate leaders require context
Among distinct current teams, for example, **GT's 47 wins in 77 decided games (61.0%)** and **CSK's 148 wins in 265 decided games (55.8%)** are different historical samples: their eras, team continuity and match counts are not matched. They must not be described as 'GT is unquestionably stronger than CSK'.

**Sports interpretation:** The app makes denominators explicit and provides a season slider, head-to-head record and phase-rate comparisons.

### 4. Venue records require identity cleaning and non-causal language
**60 raw ground strings** were conservatively grouped into **44 ground labels**. Some are venue aliases; others remain unchanged because identity was uncertain. The app does not automatically infer home advantage from where a franchise has most often appeared.

**Sports interpretation:** Many IPL matches occurred at neutral grounds, during schedule relocations or unusual seasonal environments. Ground records should be compared within season and opposition where practical.

### 5. Cricket result labels must distinguish regular wins, Super Overs and no-results
Failing to recover final Super Over winners would bias descriptive franchise win rates and model labels; counting unresolved results as losses would be worse. We use the authoritative Cricsheet `eliminator` field when available and preserve unresolved records as unresolved.

## AI prediction strategy and boundaries
The **four integrated saved models** come from Phase 3D and are **fixed-checkpoint classification models** (one match-level prediction per checkpoint; subject to innings eligibility). Reported retrospective holdout results for 2025–2026:

| Task | Observed accuracy | Status |
|---|---:|---|
| Chase win after 10 overs | 82.35% | Retrospective qualified |
| Chase win after 15 overs | 90.00% | Retrospective qualified |
| Chase win after 18 overs | 90.82% | Retrospective qualified |
| First innings total ≥180 after 10 overs | 82.07% | Retrospective qualified |

**Scientific limit:** Those same 2025–2026 seasons were examined across earlier iterative development, so these are *not* pristine blind holdouts at the full research-project level. Future untouched-season verification, class-baseline comparison, calibration and uncertainty reporting are essential. No pre-match winner predictor is presented as meeting the 70% rule.

## Recommended analyst questions to demonstrate
1. Did a franchise's batting overperform its contemporary league run rate in the powerplay and underperform in the death overs?
2. Is the franchise's chase record supported by enough decided matches to be meaningful?
3. Does an apparently favourable venue record persist after narrowing to recent seasons?
4. Which batters have contributed most total runs, and are rankings sensitive to required batting opportunities?
5. If a chase is 90/3 after 10 overs needing 181, what estimated chase probability does the checkpoint-specific ML engine output, and what historical conditions does it *not* know?

## What has not been established
No validated independent 70%+ *pre-match* prediction, causal home-ground or toss advantage, injury-informed prediction, true live-score ingestion, complete historical auction market, verified starting XIs or fully opponent-adjusted player strength. These are legitimate future scope, not capabilities to imply are already delivered.
