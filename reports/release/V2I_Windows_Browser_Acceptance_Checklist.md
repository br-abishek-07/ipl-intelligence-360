# V2-I: Live Browser Acceptance Checklist

Use after extracting the ZIP and launching `py -m streamlit run app.py` in a fresh directory. This is a human acceptance protocol, not proof that the release passed a browser test.

| ID | Test on Windows | Expected result | Sign-off |
|---|---|---|---|
| UI-01 | Open Home at 1920×1080 and 1366×768 | Cards, sidebar and hero visible without clipping | [ ] |
| UI-02 | Open League EDA, change season then venue | KPIs, charts, leaderboards and analyst notes update consistently | [ ] |
| UI-03 | Open all ten team pages | No red error boxes; logos or readable offline fallbacks | [ ] |
| UI-04 | Change team-specific season, opponent and venue | Metric sample and associated charts are synchronized | [ ] |
| UI-05 | Expand and export a scatter, grouped bar and area chart | Full-screen modal usable; HTML/PDF/image handling as provided | [ ] |
| UI-06 | Inspect CSK logo while online and offline | Official-hosted image where available; fallback otherwise | [ ] |
| UI-07 | Open Player Intelligence and change player | All tabs render; sparse sample warnings are clear | [ ] |
| UI-08 | Team DNA: toggle seasons and teams | Radar and tactical KPIs update; percentiles not called accuracy | [ ] |
| UI-09 | AI Prediction: run 4 supported states | No errors; probabilities numeric, 0–100%; charts have titles | [ ] |
| UI-10 | AI Prediction: provide invalid inputs | Clear validation warning; no crash or fake estimate | [ ] |
| UI-11 | Check responsive UI at ~390px wide | No clipped filters or unreadable KPIs | [ ] |
| UI-12 | Turn on reduced motion | Animations stop; usability remains intact | [ ] |
| UI-13 | Open Capstone Research & Viva Centre | Architecture renders; files download | [ ] |
| UI-14 | Run `python scripts/release/capstone_release_audit.py` | All integrity/model reproduction checks pass | [ ] |
| UI-15 | Optional `python -m pytest -q` (dev requirements) | Existing regression suite passes | [ ] |

**Bug report template:** page | filter values | screenshot | traceback/PowerShell output | expected behavior | observed behavior.

**Do not present unchecked boxes as finished browser QA.**
