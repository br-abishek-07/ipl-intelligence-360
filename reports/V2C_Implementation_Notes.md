# V2-C — Franchise Intelligence / Sports Analyst Upgrade

## What has changed

- All ten existing franchise Streamlit routes now call one new engine `dashboard/franchise_v2.py`; the other league, comparison, AI and methodology pages have not been removed.
- Team colors come from the existing V2 theme tokens, preserving the neutral league palette.
- Twelve glass KPI cards per team, plus seven analysis tabs: Legacy & achievements; Results & seasons; Batting; Bowling; Franchise legends; Rivals & grounds; Match evidence & download.
- Sidebar filter intersection: **season range, opponent(s), venue(s), match stage(s), selected team's result, batting/chasing role, toss win/loss and match participation of an identified player**. All active team stats, legends, phase charts, opponent/venue tables and exports are limited to the same unique match IDs.
- Player selection uses Cricsheet registry ID and participation. Such player lists may contain Impact Players and **are not equivalent to confirmed starting XI**.
- Franchise title years, champion/finalist records and playoff-participation seasons are computed only from recorded matches. The all-time trophy cabinet does not change with the sidebar scope, and is explicitly labeled as such.
- Batting leaders: total batter runs in selected matches; bowling leaders: only bowler-credited wickets. Bowling-phase wicket totals count all team dismissals. These two wicket definitions should **not** be interchanged.
- Sports analyst briefings use observations from the current selected match set and flag small samples, without causal claims.
- Existing four experimental/retrospectively qualified prediction models are unchanged and remain available in the integrated app.

## Metric dictionary

| Metric | Formula / guardrail |
|---|---|
| Team matches | Distinct `team_match_summary.match_id` after all intersected franchise filters |
| Team wins / losses | Final results including recorded Super Over resolutions; no-results excluded from losses |
| Win % | 100 × wins / decided team matches |
| Trophy count | Number of recorded IPL Finals won; deliberately calculated all-time, not filtered |
| Final appearances | Unique IPL `Final` matches involving the franchise, all-time |
| Playoff seasons | Unique seasons with at least one explicitly played qualifying/elimination/semi-final/final match; not inferred from rankings |
| Runs scored / conceded | Team runs summed across regulation innings in the selected matches |
| Batting run rate | Six × runs scored / legal balls faced |
| Bowling conceded rate | Six × opposition runs / legal balls bowled |
| Wickets taken | Wickets lost by the opposing batters including run-outs and other fielding dismissals |
| Player wicket leader | Bowler-credited wickets only; not all opponent dismissals |
| Boundary percentage | 100 × (fours + sixes) / team legal balls faced; different from per balls batter-faced |
| Highest innings total | Maximum `innings_summary.runs` for a selected team batting innings |
| Phase rates | Powerplay: 1–6, middle: 7–15, death: 16–20, per six legal balls |

## Data provenance and required missing information

The all-time records file `reports/V2C_Team_AllTime_Records.csv` and `reports/V2C_Franchise_Dossiers.json` are created by `scripts/build_v2c_reports.py` from bundled Cricsheet-derived files. IPL Final records also count championships won by historical franchises not among the ten active franchise routes. Delhi Capitals includes Delhi Daredevils history, Punjab Kings includes Kings XI Punjab history, and Royal Challengers Bengaluru includes Royal Challengers Bangalore history; historic defunct teams are not merged.

The Cricsheet match JSON contains player participant lists, **not captains**. To prevent false best-captain rankings, those cards remain unavailable without evidence. An optional import file `data/metadata/captaincy_match_registry.csv` may be populated from carefully verified scorecard sources using the included blank template. The importer rejects duplicated match-team captains, uncited rows and captain IDs not on a matching franchise match participant list. A structural check cannot determine that a cited webpage is correct; humans must review those sources.

Official team logos, player images and IPL trophy photography are **not licensed or embedded**. The ten offline SVG monograms are original, decorative replacements only. Sourcing and image permissions are scoped to the subsequent V2-D asset milestone.

## Review checklist

1. In **League EDA**, confirm original neutral palette and global slicers continue working.
2. In **CSK Analyst Desk**, change seasons and confirm all 12 filtered KPIs, run/wicket legends, phase charts, rival/venue tables and CSV exports change together.
3. Verify trophy titles and years stay all-time even when a single-year filter is selected.
4. Select an opponent, ground, result and participant together; if no fixtures match, the page should display an empty-state warning rather than fabricate results.
5. Repeat on other franchise routes (MI, RCB, KKR, SRH, RR, DC, PBKS, GT, LSG); theme changes and relevant data appears.
6. Run `python -m pytest tests -q` and the notebook `notebooks/V2C_Franchise_Intelligence_EDA.ipynb`.
7. Launch actual Streamlit on a laptop and check responsiveness/plotly rendering. Automated screen tests in this environment use a Streamlit test double; the separate HTML concept is not proof of actual Streamlit rendering.
