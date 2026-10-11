# IPL Rage-Bait Debate Lab — Numbers First

These are deliberately provocative questions, **not proofs of an overall GOAT ranking or causal effect**.
All figures are calculated from the supplied Cricsheet-derived IPL match tables through 2026. Competition-specific totals and incomplete historical captaincy data are clearly labelled.

## 1. 🔥 Rohit is a greater IPL BATTER than Kohli because MI has more trophies — seriously?
**Verdict:** Not on career batting production: Kohli has 9,336 runs and 9 hundreds; Rohit has 7,329 runs and 2 hundreds.
**Audit evidence:** Kohli: 9,336 runs / 275 batting matches / SR 134.80. Rohit: 7,329 runs / 275 batting matches / SR 132.92. Team trophies are not individual batting statistics.
**Source tables:** `batting_player_match.csv; finals registry`
**Limitations:** Individual batting and captaincy are distinct; batting position and role also differ.

## 2. 🔥 What if ABD, not Kohli, is IPL’s real match-winning batting icon?
**Verdict:** ABD scores much faster (SR 151.69 versus Kohli 134.80) and has 25 recorded Player-of-the-Match awards versus Kohli’s 22. Kohli leads massively on career runs.
**Audit evidence:** AB de Villiers: 5,162 runs, 3,403 balls, 170 batting matches, 25 awards. Kohli: 9,336 runs, 6,926 balls, 275 batting matches, 22 awards.
**Source tables:** `batting_player_match.csv; player_of_match_awards.csv`
**Limitations:** Strike rate and awards reflect different roles and contexts; neither alone defines a “GOAT”.

## 3. 🔥 Dhoni better than Kohli as a BATTER — or just the bigger icon?
**Verdict:** Kohli owns the run-volume comparison (9,336 vs 5,439), while Dhoni’s career strike rate is slightly higher (137.45 vs 134.80). The data gives no universal batting-GOAT verdict.
**Audit evidence:** Kohli 275 batting matches, 9,336 runs; Dhoni 241 batting matches, 5,439 runs. Total strike rates are calculated from recorded batter runs and balls.
**Source tables:** `batting_player_match.csv`
**Limitations:** Different batting positions, eras, not-outs and entry situations invalidate a one-number “better” ranking.

## 4. 🔥 Did Rajat Patidar accomplish more as RCB title-winning captain than Kohli ever did?
**Verdict:** In the verified IPL finals registry, Patidar captained 2 RCB championship wins (2025, 2026); Kohli captained 0 title-winning finals. This is a *trophy-final statistic*, not proof of total leadership quality.
**Audit evidence:** RCB final-win captain records: 2025, 2026 for Patidar. Kohli’s 2016 RCB final is recorded as runner-up.
**Source tables:** `verified_finals_captains_2008_2026.csv`
**Limitations:** Complete match-by-match captaincy win rates are not yet verified; do not assert an overall best captain.

## 5. 🔥 Dhoni or Rohit: who actually won more IPL crowns as captain?
**Verdict:** They are level on IPL championship-winning finals: Dhoni 5, Rohit 5. “Five titles proves one is greater” does not discriminate between them.
**Audit evidence:** Dhoni winning finals 2010, 2011, 2018, 2021, 2023. Rohit winning finals 2013, 2015, 2017, 2019, 2020.
**Source tables:** `verified_finals_captains_2008_2026.csv`
**Limitations:** Only captained finals are compared; team quality, league wins and other captaincy decisions are not evaluated.

## 6. 🔥 MI is the undisputed GOAT franchise? CSK’s win rate says HOLD ON.
**Verdict:** MI and CSK each have 5 IPL titles, but CSK won 148/265 decided matches (55.85%), against MI’s 157/291 (53.95%).
**Audit evidence:** Championships: CSK [2010, 2011, 2018, 2021, 2023], MI [2013, 2015, 2017, 2019, 2020]. CSK win rate 55.85%; MI 53.95%.
**Source tables:** `team_match_summary.csv; verified_finals_captains_2008_2026.csv`
**Limitations:** Win percentage and titles capture different dimensions; differing matches/seasons reduce direct comparability.

## 7. 🔥 CSK is superior to MI? Then explain MI’s head-to-head edge.
**Verdict:** MI won 21 and CSK won 20 of their 41 decided meetings. That is a one-match advantage—not domination.
**Audit evidence:** MI head-to-head: 21 wins, 20 losses, 41 decided meetings, 2008–2026.
**Source tables:** `team_match_summary.csv`
**Limitations:** One-match difference in a long rivalry does not establish future superiority.

## 8. 🔥 RCB fans talk dominance. Why does CSK lead this rivalry 21–14?
**Verdict:** CSK won 21 of 35 decided IPL meetings with RCB, while RCB won 14.
**Audit evidence:** CSK–RCB decided matches: 35; CSK wins 21; RCB wins 14.
**Source tables:** `team_match_summary.csv`
**Limitations:** All-time results mix different rosters and phases of team history; evaluate specific seasons separately.

## 9. 🔥 Still calling RCB “trophyless”? Have you looked at 2025 AND 2026?
**Verdict:** The verified finals records list 2 RCB IPL titles: 2025, 2026. Their decided-match record is 145/283 (51.24%).
**Audit evidence:** Final victories: [2025, 2026]. Decided RCB matches: 283, wins 145.
**Source tables:** `verified_finals_captains_2008_2026.csv; team_match_summary.csv`
**Limitations:** A recent title run overturns the “trophyless” claim but does not retroactively settle earlier criticisms.

## 10. 🔥 GT has a better all-time win rate than CSK AND MI. Are the old giants overrated?
**Verdict:** GT: 47/77 (61.04%); CSK: 148/265 (55.85%); MI: 157/291 (53.95%).
**Audit evidence:** All-time decided matches: GT 77, CSK 265, MI 291.
**Source tables:** `team_match_summary.csv`
**Limitations:** GT has a much shorter participation history; compare overlapping seasons for a fairer direct assessment.

## 11. 🔥 “Mr IPL” Raina or Dhoni: who actually scored more FOR CSK?
**Verdict:** In recorded CSK batting matches, Dhoni scored 4,865 to Raina’s 4,687. Dhoni played 214 batting matches for CSK; Raina 171.
**Audit evidence:** Dhoni at CSK: 4,865 runs, 3,497 balls; Raina at CSK: 4,687 runs, 3,424 balls. Franchise-only totals, not complete IPL careers.
**Source tables:** `batting_player_match.csv`
**Limitations:** Total runs favour longer participation and role/opportunity; do not infer who had the superior peak.

## 12. 🔥 Why crown Bumrah IPL’s wicket king when Chahal has MORE wickets?
**Verdict:** Chahal has 233 credited wickets, Bumrah 187. Bumrah has a lower economy (7.34 versus 8.05 runs/over).
**Audit evidence:** Chahal: 233 wickets / 184 bowling matches / economy 8.05. Bumrah: 187 / 158 / economy 7.34.
**Source tables:** `bowling_player_match.csv`
**Limitations:** Leg-spin versus pace and phase/ground use differ; wicket count is not a direct quality ranking.

## 13. 🔥 Bumrah surpassed Malinga? The wickets-per-match numbers challenge that.
**Verdict:** Malinga took 170 wickets in 122 bowling matches (1.39/match); Bumrah 187 in 158 (1.18/match). Malinga also has a marginally lower recorded economy.
**Audit evidence:** Malinga economy 7.14, 2827 legal balls; Bumrah economy 7.34, 3631 balls.
**Source tables:** `bowling_player_match.csv`
**Limitations:** Different playing eras and team strategies; not proof Malinga is definitively better.

## 14. 🔥 Toss wins matches? Then why is it almost a COIN FLIP?
**Verdict:** The toss-winning side won 634/1,234 decided matches (51.38%). Barely more than half.
**Audit evidence:** One record per decided IPL match. Toss-winning side won 634 matches and lost 600.
**Source tables:** `matches_enriched.csv`
**Limitations:** Association alone cannot estimate causal toss advantage; pitch/dew/toss decision matter.

## 15. 🔥 Chasing is a guaranteed IPL hack? The scoreboard disagrees.
**Verdict:** Chasing sides won 672 of 1,234 decided matches (54.46%). A modest historical advantage, not a cheat code.
**Audit evidence:** Chase wins 672; chase losses 562 across 1,234 decided matches.
**Source tables:** `team_match_summary.csv`
**Limitations:** Chasing record varies with ground, season, target size, and match conditions.

## 16. 🔥 A 200+ total is “UNCHASEABLE”? Tell that to the 51 losing teams.
**Verdict:** Of 213 eligible first-innings totals of 200+, the batting-first side won 162 and lost 51 (23.9% defeats).
**Audit evidence:** Eligibility: non-DLS decided matches with at least 100 legal first-innings balls. 200+ cases 213; defend wins 162; losses 51.
**Source tables:** `innings_summary.csv; matches_enriched.csv`
**Limitations:** A team scoring 200+ usually wins; this debunks a guarantee, not the strong advantage.

## 17. 🔥 200 is the new 160? IPL 2026 has made old batting benchmarks look ancient.
**Verdict:** 200+ first innings occurred in 4/56 eligible games in 2016 (7.1%), versus 37/70 in 2026 (52.9%).
**Audit evidence:** Same eligibility in both seasons: non-DLS, decided matches, >=100 legal first-innings balls. Threshold exactly 200 runs.
**Source tables:** `innings_summary.csv; matches_enriched.csv`
**Limitations:** Era comparison is descriptive; rule changes, batting approach and venue composition may contribute.

## 18. 🔥 “Powerplay doesn’t matter.” Explain the 1.10 runs-per-over gap.
**Verdict:** Across 2022–2026 non-DLS decided games, winning teams scored 9.70 per over in the powerplay against 8.60 for losing teams, a difference of 1.11.
**Audit evidence:** Winning-team batting powerplays n=358; losing-team batting powerplays n=358, 36 legal balls per observation.
**Source tables:** `team_phase_match.csv; team_match_summary.csv`
**Limitations:** Results show association; winning teams may differ in skill, target, toss and opposition.

## 19. 🔥 MI fans mocked CSK’s 2026 season. But who actually won MORE matches?
**Verdict:** In 2026, CSK won 6/14 decided matches (42.9%), while MI won 4/14 (28.6%).
**Audit evidence:** Season=2026; one row per team and decided match. No-result matches excluded.
**Source tables:** `team_match_summary.csv`
**Limitations:** Single-season team records are relatively small samples; should not overwrite long-term history.
