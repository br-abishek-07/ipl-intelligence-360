# V2-A + V2-B Implementation & Sports-Analysis Notes

## Completed

### Professional design language
- Neutral deep-navy background, golden league accent and royal-blue secondary.
- Ten tokenized team themes applied when a franchise route is opened.
- HTML/CSS glass KPI cards and accessible fallback monogram emblems.
- Motion restrained to nonessential hover transitions, respects `prefers-reduced-motion`.
- Real Streamlit app source: `dashboard/design.py`, `dashboard/views.py`, `dashboard/league_v2.py`.

### Synchronized league slicers
- Scope is a set of distinct Cricsheet match IDs.
- Intersections: seasons ∩ team fixtures ∩ venue ∩ match stage ∩ toss decision ∩ team innings role ∩ team outcome.
- 12 scoped KPI cards, six chart modules, live recalculation of analyst narrative, and match/innings/phase exports.
- A franchise-specific **player leaderboard** intentionally uses only that franchise's players, while league-wide match totals continue to include both sides. That distinction is labeled in the UI.

### Cricket integrity
- When a user's filters identify an unfinished/no-result game, it contributes to raw runs and deliveries but **not** to decided-match win ratios.
- Super Over wins are resolved in the original cleaned match source but Super Over deliveries are not folded into ordinary cricket scoring totals.
- Wickets lost by a batting team and wickets officially credited to bowlers are distinct counts.
- Over segments: powerplay overs 1–6, middle overs 7–15, death overs 16–20; denominators are legal balls.
- No automatic claim of home advantage, pitch causation, captain ranking, official trophy rights, or player image provenance.

## Accuracy of selected scope

A selected season should reduce **every** league metric, all figure data and descriptions. Yearwise player/phase summary tables from V1 would be misleading under venue/stage slicers. Therefore the new match-phase mart reaggregates all individual deliveries by match ID/innings and creates a new player ranking from the *per-match* batting/bowling tables.

## Remaining tasks and sources

A team-by-season captain registry is still needed to identify leaders reliably. Cup years on team dashboards are restricted to IPL `Final` rows, while captaincy success should remain unknown without a validated source. League metadata/source images need a separate licensing and audit manifest. Current team badges are decorative original SVG monograms and not replacements for official identities.

## Reproducible evidence

Run `python -m pytest tests -q`, `python scripts/build_match_phases.py` and `python scripts/create_v2_notebook.py`. Compare the audited output to `reports/V2_QA_Report.json`. For UI user-acceptance review, launch Streamlit with the documented commands and test season/team/venue/stage combinations manually. HTML visual preview is a **design prototype** rather than the actual production UI.
