# Deployment V4Z to GitHub and Streamlit Community Cloud

## Prerequisite: upload complete distribution

**The README and rebuild documentation may be present before the application source. Do not deploy until you see app.py and all required folders in the repository root.** The 13 MB public-ready archive contains over 200 project files, including binary GZIP and model data. Commit the *extracted contents*, not the ZIP as one file.

1. Download IPL360_V4Z_Streamlit_Cloud_Ready.zip from the ChatGPT project deliverables.
2. Extract the ZIP to a local folder. Make sure app.py is inside that folder, not another nested level.
3. Install [GitHub Desktop](https://desktop.github.com/); sign in and choose File → Clone repository → br-abishek-07/ipl-intelligence-360.
4. Open the newly cloned directory.
5. Copy the extracted public-ready files/folders *into* that cloned directory. Keep the newer README.md and docs/ documentation already online; if Windows asks to overwrite README.md, select **Keep existing** (or restore it from GitHub after copying).
6. Review GitHub Desktop's Changes tab carefully. There must be no secrets, credentials, .env file, .streamlit/secrets.toml or private notebook. Pay attention to source data and asset redistribution licences.
7. Set commit description to "Publish IPL Intelligence 360 V4Z public app". Select Commit to main → Push origin.
8. Refresh [GitHub repository](https://github.com/br-abishek-07/ipl-intelligence-360). Check app.py, requirements.txt, .python-version, .streamlit/config.toml, dashboard/, pages/, data/, reports/, models_portable/, and assets/ are present.

If GitHub refuses files >100 MB, investigate that file. The intended deployment bundle was designed to be far smaller overall, but other large source files should not be added without checking licensing and necessity.

## Streamlit deployment

1. Visit https://share.streamlit.io/ and sign in with GitHub.
2. Select **Create app** → existing app.
3. Repository: **br-abishek-07/ipl-intelligence-360**.
4. Branch: **main**.
5. Main file path: **app.py**.
6. Python: **3.12** if selectable.
7. Deploy, then inspect build logs and verify the public URL and app sharing settings.

## Live acceptance criteria

- Open the public site while *logged out* (incognito).
- All ten franchise pages work and their 2026 squad panels are sourced historical snapshots.
- Year, venue, opponent and stage filters change related KPIs and visualizations.
- Player Intelligence searches work for V Kohli and KD Karthik.
- Portable chase/score prediction outputs load with reasonable numeric inputs.
- Team DNA and Match Replay update for the selected seasons/matches.
- Report Studio exports a valid PDF and CSV evidence bundle.
- Fan Wars presents 19 questions with evidence and caveats.
- Charts offer the intended fullscreen controls; no duplicate Streamlit keys.
- Application logs have no credential leak or load-time errors.

## Common problems

**ModuleNotFoundError:** requirements.txt must be at root, and all packages must be compatible with selected Python version.

**FileNotFoundError:** Linux paths are case sensitive; do not omit zipped CSV/GZIP files, images or directories. Ensure all locations are relative to the project root.

**Out-of-memory:** Streamlit Community Cloud has resource limits. Cache static loads and test a page that reads raw deliveries, then consider reducing what is loaded per user session.

**Missing logos:** some visual assets are remote or subject to redistribution restrictions. Use fallback badges and verify official logo asset URLs.

**Blank/slow startup:** open Streamlit app logs and check for timeouts, memory and excessive cache initialization.

**No public link:** GitHub upload and a successfully deployed Streamlit app are separate actions. A GitHub repo URL is **not** a hosted dashboard URL.

## Protect data, intellectual property and claims

Do not publish API tokens, user data or unlicensed imagery. Cricsheet provides match data and identifiers; attribute appropriately and check terms at https://cricsheet.org/. Avoid portraying independent student research as an official IPL franchise application. Metrics are historical; an old holdout is not a promise of future accuracy.
