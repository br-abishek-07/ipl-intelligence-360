# V2-I Final Capstone Release Notes

## Scope completed

- Integrated a **Capstone Research & Viva Centre** at sidebar page 18, linked from Home.
- Prepared an editable academic report, a six-page PDF, a 15-slide PPTX, a vector-style architecture image and three historical EDA/model charts.
- Added a rerunnable release integrity and time-measurement audit, an installer checklist and a reproducible viva defense guide.
- Cached immutable Player-of-the-Match award records across franchise rerenders.
- Kept source archive, team phase records, all four portable models, franchise dashboards, full-screen chart controls and Team DNA unchanged.

## Automated QA measured

- 159 existing-and-new regression tests passed **excluding** the extra full-dashboard simulated render.
- The full-suite run got to that final render with no reported failures but timed out; it must not be reported as fully passed.
- 36/36 offline source integrity and model reproduction checks passed.
- PowerPoint converted to a 15-page PDF for slide layout inspection; Word report rendered to six page PNGs and a PDF and visually checked.
- Actual Streamlit browser interaction, mobile responsiveness, online official logos and download actions require Windows browser sign-off.

## Model transparency

Retrospective classification accuracy is 82.35% for chase at 10 overs, 90.00% for chase at 15, 90.82% for chase at 18, and 82.07% for first-innings 180+ at 10 overs. These figures are **not** independently blind new-season proof; 2025–2026 were reviewed iteratively. Majority baseline, Brier and ROC-AUC are provided in the report.

## Source integrity

`reports/release/V2I_Release_Audit.json` contains SHA256 and file sizes for the three immutable data assets and four portable checkpoint model artifacts. It can be rechecked with `python scripts/release/capstone_release_audit.py`.
