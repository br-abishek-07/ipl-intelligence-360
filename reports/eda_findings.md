# IPL EDA — Verified descriptive findings

Source: Cricsheet IPL archive and Phase 2 standardized records. 1,243 matches from 2008–2026; 295,557 regulation deliveries.

- 16 tied matches have a verifiable Super Over eliminator winner reconstructed from official Cricsheet JSON; 9 matches still have no winner.
- 557 match/team personnel lists differ from exactly 11; these are **not treated as confirmed pre-match XIs**.
- 60 raw venue labels reduce to 44 grouped labels through the documented, conservative normalization rules.

## Season scoring (eligible regulation first innings: >=100 legal balls, no DLS)

- 2022: 74 matches; 72 eligible first innings; mean score 173.6, median 170.
- 2023: 74 matches; 72 eligible first innings; mean score 182.2, median 182.
- 2024: 71 matches; 70 eligible first innings; mean score 190.1, median 186.
- 2025: 74 matches; 68 eligible first innings; mean score 195.2, median 198.
- 2026: 74 matches; 70 eligible first innings; mean score 197.5, median 201.

## Current franchise profiles (all available seasons; resolved results only)

- CSK: 266 matches, 265 resolved, 148 wins (55.8%).
- MI: 291 matches, 291 resolved, 157 wins (54.0%).
- RCB: 286 matches, 283 resolved, 145 wins (51.2%).
- KKR: 278 matches, 276 resolved, 142 wins (51.4%).
- SRH: 211 matches, 210 resolved, 103 wins (49.0%).
- RR: 251 matches, 249 resolved, 125 wins (50.2%).
- DC: 281 matches, 277 resolved, 129 wins (46.6%).
- PBKS: 278 matches, 275 resolved, 129 wins (46.9%).
- GT: 77 matches, 77 resolved, 47 wins (61.0%).
- LSG: 72 matches, 71 resolved, 34 wins (47.9%).

## Interpretation guardrails
- Franchise records do not imply equal sample sizes, eras, player strength or venue conditions.
- Older names Delhi Daredevils→DC and Kings XI Punjab→PBKS are handled by the Cricsheet team codes. Historic, discontinued franchises stay distinct.
- Batting phase rates include all team runs and use legal balls as denominator.
- Bowler wickets exclude run outs and non-credit dismissal kinds.
- Do not interpret toss association as proof of causation.
- Auction records are historical and incomplete; do not interpret them as a complete market.
