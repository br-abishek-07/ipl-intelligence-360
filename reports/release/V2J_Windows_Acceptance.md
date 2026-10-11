# IPL Intelligence 360° — Final Windows Browser Acceptance (V2-J)

**Do not tick any test unless you actually completed it on the real Streamlit app.** No browser tests were run in the offline build environment because Streamlit was unavailable. Use Windows Chrome or Edge at full screen (1366×768 and 1920×1080) and also ~390px responsive width.

| Test | What to do | Expected result | Sign-off |
|---|---|---|---|
| UI-01 | Launch from clean folder | No errors in terminal; landing loads | [ ] |
| UI-02 | League EDA: change season, team and venue | KPI/leaderboards/charts reflect all selected filters | [ ] |
| UI-03 | Open CSK and each of 9 other franchise pages | No red Streamlit errors; theme/branding works | [ ] |
| UI-04 | Change franchise year, opponent and venue | Charts/KPIs change together, all-time awards explicitly stable | [ ] |
| UI-05 | Check CSK logo online and offline | Valid IPL logo online, documented fallback offline | [ ] |
| UI-06 | Expand scatter, bar, area, line, and stacked charts | Full-screen modal readable with image/HTML export | [ ] |
| UI-07 | Try Players: Virat Kohli, MS Dhoni, KD Karthik | Search and player switch work without retaining bad filters | [ ] |
| UI-08 | Try selected rare player + filters | Empty/small sample is identified, not extrapolated falsely | [ ] |
| UI-09 | Records & Legends | Correct trophy/runs/wicket source definitions | [ ] |
| UI-10 | Team DNA season/team selector | Radar and descriptive percentiles update; no causality claims | [ ] |
| UI-11 | AI predictions: four supported checkpoints | Valid probabilities, explanatory text, chart titles/expand controls | [ ] |
| UI-12 | AI predictions: unsupported states | Clear input eligibility message, no misleading output | [ ] |
| UI-13 | AI → Earlier Live Model Audit | Shows research-only disclosure, figures, full-screen comparison | [ ] |
| UI-14 | Data Quality Centre + Capstone Guide | Errors/limitations and report downloads are visible | [ ] |
| UI-15 | 1366×768, 1920×1080, ~390px | No overlapping titles, clipped KPI values or unreadable charts | [ ] |
| UI-16 | Reduced-motion OS setting | Animations become restrained/disabled | [ ] |
| UI-17 | Download report, PPT and selected CSV | Files open; no empty outputs | [ ] |
| UI-18 | Restart dashboard from fresh terminal | Results persist, startup is stable | [ ] |

## QA sign-off
- Tested on date:
- Browser and version:
- Python version (`py --version`):
- Streamlit version (`py -m streamlit version`):
- Defects / screenshots:
- Reviewer:

## Report a defect
Share (1) page name, (2) exact filter values, (3) screenshot, (4) complete terminal error, and (5) expected vs observed behavior. No project credentials or personal information in screenshots.
