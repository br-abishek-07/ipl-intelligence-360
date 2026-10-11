# V2-D — Sports Analyst Visualization Guide

**Project:** IPL Intelligence 360° / AI-Driven Data Science Capstone  
**Build stage:** V2-D — franchise visuals + IPL-hosted logo integration

## Design principles

Each of the ten franchise pages keeps the existing eight page slicers, and **all selected-match figures originate from exactly the same selected match ID set**. Only the trophy cabinet and historical honours are intentionally all-time. This prevents misleading filtered/unfiltered comparisons. Quantities are sourced from the Cricsheet JSON archive supplied by the student, with historical team continuity as defined in the earlier cleaning pipeline.

## KPI ribbon — 16 metrics

- Matches, wins, win ratio, **all-time** trophies
- Runs scored, batting run rate, wickets taken, opposition run rate
- Batting boundary frequency, sixes, highest innings total, no-results
- Mean runs per recorded innings, total runs scored less runs conceded
- Chase win ratio and batting-first win ratio (decided games only)

**Denominators**: Win % excludes ties/no-results without recorded winner; chase/defence % excludes undecided matches. Batting and opposition runs reflect recorded regulation innings and can be affected by DLS, shortened contests and match context. Trophy count is not recalculated when filtering by season.

## Nineteen distinct graph views (across the tabs)

| # | Chart | Type | Cricket question |
|---|---|---|---|
| 1 | Seasonal wins/losses/no result | Grouped vertical bar | Which seasons had the most wins and defeats? |
| 2 | Season win percentage | Line + markers | How has conversion of matches to wins changed? |
| 3 | Last 10 decided matches | Rolling line | Was the team in a short-term winning or losing patch? |
| 4 | Average runs per selected match | Area | Have match scoring totals evolved? |
| 5 | Runs for versus runs against | Outcome-coloured scatter | What do scores look like in wins versus defeats? |
| 6 | Wins/losses + win percentage | **Combined line + clustered vertical columns**, dual axis | Are wins and win-rate telling the same story? |
| 7 | Batting rate by phase vs fixture benchmark | Grouped columns | Which batting phase appears stronger? |
| 8 | Fours and sixes by phase | Stacked columns | Where are boundaries concentrated? |
| 9 | Batting phase scoring trend | Multiline | Has the batting approach changed season by season? |
| 10 | Recorded innings runs | Histogram | What is the distribution of scores? |
| 11 | Franchise leading batters | Horizontal bars | Who supplied the most runs? |
| 12 | Batting runs vs strike rate | Bubble scatter | Which batters combine volume with intent? |
| 13 | Bowling run-rate by phase vs benchmark | Grouped columns | When does the attack concede the most? |
| 14 | Dismissals per 120 legal balls | Vertical columns | In which phase does the bowling take wickets? |
| 15 | Bowling rate by phase across seasons | Multiline | How did bowling efficiency change? |
| 16 | Top credited wicket-takers | Horizontal bars | Who took the most bowler-credited wickets? |
| 17 | Bowler wickets vs economy | Bubble scatter | Which bowlers offer wickets and economy? |
| 18 | Wins and losses by opposing team | Stacked horizontal bars | How balanced is the rivalry record? |
| 19 | Venue appearances vs win ratio | Bubble scatter | Which ground results have reasonable samples? |

### Analytical safeguards

- The phase benchmark describes **the same selected fixtures**, including the franchise; it is not a separate league-wide control sample.
- Powerplay, middle and death periods are of unequal length; absolute boundary counts cannot compare efficiency across phases. Use runs / over instead.
- For batters and bowlers, scatter plots include only players with at least **60 balls** in the selection; this controls noisy ratios but is not a minimum match-count guarantee.
- For venues, bubble charts require **at least three decided games** to avoid single-match percentage claims.
- Dot-ball, detailed bowling-type, team captaincy rankings, win-probability causality, and individual photos are **not inferred** from absent data.
- The participation filter can include Impact Players; it does not imply a confirmed starting XI.
- Player wicket totals count bowler-credited dismissals; bowling-phase dismissal totals can additionally include run-outs, so they should not be confused.

## Team theming, transparency and motion

The primary plotted series, KPI glow, tab border and header details use the selected franchise accent. Glass KPI cards retain high-contrast white labels, dark transparent panels and a gentle 5-second pulse. Entrance and hover transitions are short and intentionally subtle. The UI supports `prefers-reduced-motion: reduce`, which disables CSS animations and transitions for accessibility. Streamlit reruns are not technically continuous page transitions, so the CSS is a visual enhancement rather than a promise of fully interpolated SPA navigation.

## Official franchise marks

The app attempts to display logos through **the URL pattern used by official IPL-hosted team assets**, for example:
`https://documents.iplt20.com/ipl/MI/Logos/Roundbig/MIroundbig.png`.

**Limitation:** the build environment could not download or verify those remote images, so working online hotlinks are not guaranteed. The app layers the original team monogram art behind the official-logo URL, so it remains branded when offline. If suitable image-use permission has been obtained, save `CSK.png`, `MI.png`, etc. into `assets/logos/official/`; local files take priority and make demos fully offline.

Official franchise logos belong to their respective franchise owners; the code does not redistribute those files. The IPL brand-protection guidance and logo usage restrictions must be considered for any public deployment.

Sources:
- IPL official team directory: https://www.iplt20.com/teams
- IPL franchise image CDN as linked from IPL points table: https://staging-iplt20.epicon.in/points-table/men/google.com
- IPL brand/content protection guidelines: https://documents.iplt20.com/bcci/documents/1680174721009_Brand%26ContentProtectionGuidelines.pdf
