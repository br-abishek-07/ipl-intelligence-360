# V2-I Offline Release Audit
**Automated checks:** 36 passed / 36 total.

## Timed operations (milliseconds, three local repetitions)
| Operation | Median time | Three runs |
|---|---:|---|
| read matches csv | 7.64 | 7.16, 7.64, 7.73 |
| read team match csv | 10.24 | 8.76, 10.38, 10.24 |
| read phase csv | 9.13 | 7.2, 9.13, 9.31 |
| build csk team dna 2022 2026 | 119.40 | 94.7, 119.4, 119.71 |
| portable model inference one chase state | 0.10 | 3.28, 0.1, 0.08 |

## Automated assertions
- PASS: Packaged immutable file: data/source/ipl_json.zip
- PASS: Packaged immutable file: data/analytics/team_match_summary.csv
- PASS: Packaged immutable file: data/analytics/team_phase_match.csv
- PASS: Packaged immutable file: models_portable/chase_after_60_balls.json
- PASS: Packaged immutable file: models_portable/chase_after_90_balls.json
- PASS: Packaged immutable file: models_portable/chase_after_108_balls.json
- PASS: Packaged immutable file: models_portable/first_innings_180_after_60_balls.json
- PASS: 1,243 unique IPL matches — 1243 matches
- PASS: 19 seasons, 2008 through 2026
- PASS: Exactly two franchise match rows per match
- PASS: Team-match IDs link to source matches
- PASS: Phase rows link to source matches
- PASS: No invalid delivery run totals
- PASS: No duplicate delivery positions
- PASS: Super Over results accounted separately — 16 recovered, 9 unresolved
- PASS: Ten current franchise routes
- PASS: Team coverage in records
- PASS: Exactly four provisional checkpoint models
- PASS: Reported checkpoint accuracies >=70%
- PASS: Holdout studies flagged retrospective
- PASS: Holdout records present: chase_after_60_balls
- PASS: Accuracy reproduces for chase_after_60_balls — accuracy 0.823529; matches 136
- PASS: One prediction per match for chase_after_60_balls
- PASS: Holdout records present: chase_after_90_balls
- PASS: Accuracy reproduces for chase_after_90_balls — accuracy 0.900000; matches 130
- PASS: One prediction per match for chase_after_90_balls
- PASS: Holdout records present: chase_after_108_balls
- PASS: Accuracy reproduces for chase_after_108_balls — accuracy 0.908163; matches 98
- PASS: One prediction per match for chase_after_108_balls
- PASS: Holdout records present: first_innings_180_after_60_balls
- PASS: Accuracy reproduces for first_innings_180_after_60_balls — accuracy 0.820690; matches 145
- PASS: One prediction per match for first_innings_180_after_60_balls
- PASS: Chart viewer has interactive full-screen control
- PASS: Player Intelligence page shipped
- PASS: Team DNA page shipped
- PASS: Captaincy disclaimer exists

## Scope and caveats
- This is an **offline functional and data integrity audit**. It does not test the real Streamlit browser or predict internet performance.
- Timing is hardware-dependent and is not a user-facing latency guarantee.
- The accuracy checks reproduce supplied retrospective holdout files, not fresh unseen seasons.
