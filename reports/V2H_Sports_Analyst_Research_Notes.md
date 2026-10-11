# V2-H Sports Analyst Findings and Methodology

## Scope and evidence
Historical, match-level Cricsheet 2022–2026 for the ten currently active IPL teams. Player availability, bowling speed, captaincy and pitch quality are **not** estimated. Data contains 1,243 source IPL matches overall (2008–2026); selected windows are narrower.

## Comparable team perspective
Every franchise uses its own selected match set. Season/venue/stage-matched **independent** games played by other current franchises are the comparison set. The excluded target matches help prevent circular comparison. This does not statistically control for opponent difficulty or other confounders.

## Interpreting rankings
Six DNA axes use directional empirical percentile, subject to minimum qualifying balls/chases and five peer teams. A score of 90 indicates high historical *relative standing*, not 90% predictive accuracy, and can change with filters.

## Descriptive metric summary for 2022–2026

| Team   | Selected seasons   |   Matches |   Decided games |   Wins |   Win rate (%) |   Batting rate (runs/over) |   Bowling rate conceded (runs/over) |   Wickets / 120 balls |   Chasing win rate (%) |   Qualified DNA dimensions |
|:-------|:-------------------|----------:|----------------:|-------:|---------------:|---------------------------:|------------------------------------:|----------------------:|-----------------------:|---------------------------:|
| CSK    | 2022–2026          |        72 |              71 |     31 |          43.66 |                       9.03 |                                8.97 |                  6.35 |                  46.67 |                          6 |
| MI     | 2022–2026          |        74 |              74 |     30 |          40.54 |                       9.31 |                                9.46 |                  6.5  |                  42.86 |                          6 |
| RCB    | 2022–2026          |        76 |              76 |     45 |          59.21 |                       9.57 |                                9.32 |                  6.69 |                  64.71 |                          6 |
| KKR    | 2022–2026          |        69 |              67 |     34 |          50.75 |                       9.31 |                                9.08 |                  6.76 |                  52.94 |                          6 |
| SRH    | 2022–2026          |        73 |              72 |     34 |          47.22 |                       9.55 |                                9.65 |                  6.15 |                  47.06 |                          6 |
| RR     | 2022–2026          |        76 |              76 |     39 |          51.32 |                       9.42 |                                9.26 |                  6.2  |                  51.35 |                          6 |
| DC     | 2022–2026          |        71 |              69 |     33 |          47.83 |                       9.07 |                                9.4  |                  6.15 |                  45.24 |                          6 |
| PBKS   | 2022–2026          |        74 |              71 |     35 |          49.3  |                       9.59 |                                9.55 |                  6.14 |                  60    |                          6 |
| GT     | 2022–2026          |        77 |              77 |     47 |          61.04 |                       9.2  |                                9.12 |                  6.92 |                  65.12 |                          6 |
| LSG    | 2022–2026          |        72 |              71 |     34 |          47.89 |                       9.07 |                                9.35 |                  6.06 |                  41.94 |                          6 |

## Insights users can verify in the dashboard
- Compare powerplay, middle and death batting rates against weighted peer rates. Look for gaps that recur across seasons.
- Compare scoring efficiency to bowling economy with the inverted defensive axis to identify offense-versus-defense trade-offs.
- Inspect number of decided chases; avoid drawing conclusions from small samples.
- Opponent/venue analyses show historical results, not venue-adjusted strength or causal player influence.
- Tactical run-rate scenario is an arithmetic counterfactual with fixed phase lengths; it does not model wickets or wins.

## Capstone limitations
Venue assignment, DLS/rain, quality of opposition, Impact Player involvement, and uneven franchise founding years may affect comparisons. No claim that a high Team DNA score satisfies a 70% accuracy model gate.
