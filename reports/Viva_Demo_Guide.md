# Capstone Viva: Suggested 8-Minute Walkthrough

**Minute 0–1 — Problem and objective.** Explain why aggregate batting averages alone cannot tell a franchise where it is strong. Define league, team and predictive tasks.

**Minute 1–2 — Data engineering.** Show `data/source/ipl_json.zip` untouched, 1,243 matches, the team-match star table, strict player-ID joins, source normalization and Super Over outcome recovery.

**Minute 2–3 — Exploratory data analysis.** Open the EDA notebook; demonstrate missingness, first-innings scoring evolution, phase run rates and ground normalization. State denominators and non-causal limitations.

**Minute 3–5 — Franchise analyst desk.** Open CSK and MI as separate pages; use the season slider, win efficiency, batting/bowling phase charts, opponent comparisons, player leaders and venue patterns. Show auto-generated analyst briefing and explain what evidence supports it.

**Minute 5–6 — Comparative cricket analytics.** Use CSK vs MI in Team Comparison. Explain why weighted six-ball run rates are more meaningful than an unweighted per-match average for phase contrasts.

**Minute 6–7 — Machine learning.** Open AI Prediction Lab; use a chase checkpoint and show the probability. Explain the 70% gate, why the pre-match winner model was rejected, class imbalance and the need for genuinely untouched future-season tests.

**Minute 7–8 — Audit and scope.** Present the 11 passing automated tests, missing data/lineups caveat, original source preservation, and next improvements (confirmed XIs, domestic T20 form, opponent-adjusted performance).

## Possible examiner questions

**Q: Why not present all models?** A: Low-performing or misleadingly high-accuracy models do not pass the stricter benchmark and uncertainty gate. We show them in methodology rather than marketing them as reliable forecasts.

**Q: Why is chasing more common in a given season?** A: We report batting first vs second associations, but cannot attribute the difference to toss choice without controlling for conditions and opposition.

**Q: Why don't you use the same win % to compare GT and CSK?** A: Their seasons and matches span different eras; a fair comparison should condition on sample duration, opponent and rule environment.

**Q: What is data leakage?** A: Giving a model future scores, post-match player totals or match-event features unavailable at the prediction moment. Our retrospective EDA uses all historical data for description, while model inference preserves checkpoint inputs.

**Q: Can your prediction models guarantee >70% for the coming season?** A: No. They passed a retrospective validation gate, but the test seasons informed earlier development. Independent untouched future season evaluation is still required.
