# V3-C: Captaincy & Match Intelligence — Evidence and QA

## Verified additions

- All 19 IPL finals (2008–2026) identified from existing Cricsheet match data.
- Exactly two externally sourced captains per final; 38/38 names corroborated against the relevant Cricsheet match participant lists and player IDs.
- Trophy-winning captains are ranked by actual titles; **captaincy win percentage over all IPL matches remains unavailable**.
- 2009 Deccan Chargers championship is attributed to DCH, not SRH.
- Match replay calculations use delivery runs and wickets in source order. Innings totals reconcile, non-legal balls do not increase the legal-ball count, and Super Overs can be displayed separately.
- Franchise H2H metrics are symmetric when the franchises are swapped and no-result matches are separately counted.

## Explicit methodological limits

1. The independent source identifies captains in **final matches only**. Cricsheet's player participation does not prove captaincy for every other match.
2. Retrospective playback reveals historical deliveries. It does not estimate causal turning points or predicted win probability at each ball.
3. The over highlights are based on observed run and wicket bursts. No attribution of causality is made.
4. Runs-between-wickets segments are not certified partnerships between named batters.
5. Shortened and DLS-adjusted games have different rules; warnings are shown and stats should not be naively compared to 20-over innings.
6. Official logo URLs may require online connectivity. Offline decorative fallback retains team identities.
7. Browser animation, full-screen overlays and remote image loading still require a Windows manual visual check.
8. Existing ML benchmark accuracy is retrospective, not independently validated on a genuinely untouched future season.

## Source provenance

- Primary ball-by-ball, team, match ID and participant records: Cricsheet IPL JSON supplied by the user, preserved unmodified.
- Finals captain / runner-up captain mapping: Business Standard, May 31, 2026, https://www.business-standard.com/amp/cricket/ipl/2008-to-2026-check-full-list-of-ipl-winners-runners-up-and-their-captains-126053100390_1.html

## Test results

- **20/20** new V3-C domain tests passed.
- **186/186** regression tests passed with the longstanding full-page simulated-render smoke test deselected (not run).
- These tests do not constitute a real Streamlit browser test. The Streamlit runtime is unavailable in this build environment.
