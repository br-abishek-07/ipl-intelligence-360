# V3-C Windows Browser Acceptance (User Sign-Off)

Launch in the extracted folder: `py -m streamlit run app.py`.

## Must pass
- [ ] `app.py` exists at archive root and Streamlit Home opens without terminal errors.
- [ ] **Captaincy and Franchise Legacy** appears in the sidebar.
- [ ] Championship captain table shows 19 winning final captains by season, and the captain ID evidence is exportable.
- [ ] CSK shows 5 championship titles; MI shows 5; 2009 Deccan Chargers is separate from SRH.
- [ ] Captaincy scope explicitly reads *Finals only*, not full captain career win percentages.
- [ ] **Match Replay and Rivalry** appears in the sidebar.
- [ ] Selecting season 2026 and the final (match ID 1535465) loads the documented match.
- [ ] Moving the replay slider changes scores, visuals and wicket counts without changing the recorded final result.
- [ ] Over-by-over chart, wicket chart, and innings comparison have clear descriptive titles and working **Full screen** controls.
- [ ] Switching the historical match and selected season does not display stale innings data.
- [ ] CSK vs MI rivalry shows symmetric win counts if franchises A/B are swapped.
- [ ] Super Over toggle does not add those balls to normal 20-over statistics.
- [ ] All ten older franchise pages load; Player Intelligence search still works.
- [ ] All four original AI Prediction Lab models load and return probabilities.
- [ ] CSK and other remote team logos load or correctly show fallback images.
- [ ] No secrets or simulated financial data appear in the published app.
- [ ] Test browser full screen on laptop; check responsive layout and chart toolbars.

If any check fails, capture the Streamlit traceback and the relevant page screenshot before modifying data.
