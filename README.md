# IPL Intelligence 360° — V4Z Fact-Checked Fan Wars

**An educational IPL data-science and sports-analytics dashboard built with Python, Streamlit, Plotly, pandas and NumPy.**

**Status:** GitHub repository setup in progress. The complete app source still needs to be uploaded before deployment. No public Streamlit URL has been verified yet.

## The idea

Cricket fans debate which franchise, player or captain is greatest. Analysts need reproducible evidence: samples, game context, era, selected filters, and model validation. IPL Intelligence 360° combines historical scorecards, exploratory data analysis, predictive experiments, franchise intelligence, and a 19-question **Fan Wars: Fact Check** lab.

## Scope

- **1,243 IPL matches (2008–2026)** and **295,732 source delivery objects**, of which 295,557 are regulation-delivery records after separating Super Overs.
- Ten current-franchise analyst desks, theme-colored UI and synchronized season, opponent, venue and stage filters.
- League explorer, player intelligence, Team DNA, match replay, rivalries, coaching/CLT20 histories, and automated PDF reports.
- Four portable JSON match-state models: three chase checkpoints and one first-innings 180 threshold. Evaluations are retrospective, not future guarantees.
- Experimental bowling-deployment, participation, batter–bowler and cross-league scouting analyses, clearly separated from deployed models.
- Nineteen fact-checked cricket debates with figures and limitations.

## Run locally (after all application files are in this repository)

Use Python 3.12. From the project root:

~~~powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python preflight_public.py
python -m streamlit run app.py
~~~

On macOS/Linux activate with: source .venv/bin/activate

The root must contain app.py, requirements.txt, .python-version, .streamlit/config.toml and the dashboard/, pages/, data/, models_portable/, reports/ and assets/ directories. Extract the public-ready ZIP **contents** directly into the repository root; do not commit only the ZIP.

## Project documentation

- [Full architecture and rebuild guide](docs/REBUILD_GUIDE.md): source data and cleaning, derived tables, models, UI, evaluation, tests, reproducibility and limitations.
- [Public deployment guide](docs/DEPLOYMENT.md): GitHub upload, Streamlit Community Cloud, security and acceptance testing.

## Interpretation and sources

Historical differences do not prove causality. Cricsheet participant lists can include Impact Players, not confirmed starting XIs. The December 2025 post-auction 2026 roster snapshots are not verified ongoing registration lists. Captaincy and coaching coverage is incomplete outside sourced finals and documented coach periods. Research models that fail useful baselines are not advertised as production systems.

IPL ball-by-ball records are attributed to [Cricsheet](https://cricsheet.org/). Other source documents and source-date limitations are described in the data files and reports. Verify data and logo redistribution rights before making the source repository public. IPL/franchise names and trademarks are their owners' property. This is an independent student project, not an IPL/BCCI service.

**Deployment:** When the files are present, visit [Streamlit Community Cloud](https://share.streamlit.io/), select this repository and main branch, and set the main file path to app.py. Never upload .env or .streamlit/secrets.toml.
