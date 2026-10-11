# Public IPL Intelligence 360° — Deployment and QA checklist

## Before uploading
- [ ] Extract the whole ZIP, and confirm `app.py` is directly in the extracted root.
- [ ] Run `python preflight_public.py` — expect no missing files or syntax errors.
- [ ] Check that nothing private or restricted is in the repository: keys, credentials, personal information, copyrighted assets without rights.
- [ ] Verify historical source credits and each dataset's reuse terms. A public GitHub repository is publicly downloadable.
- [ ] Keep your full V4Z ZIP locally as a backup. The cloud bundle omits notebooks and slides by design.

## GitHub
- [ ] Create repository `ipl-intelligence-360` (suggested name) and choose Public only after reviewing contents.
- [ ] Upload extracted folder **contents**, not the ZIP. Use GitHub Desktop or `git push` for the many project files.
- [ ] Confirm online repository has `app.py`, `requirements.txt`, `.python-version`, `.streamlit/config.toml`, `dashboard/`, `pages/`, `data/`, `models_portable/`, `reports/`, `assets/`.
- [ ] `.streamlit/secrets.toml` and `.env` are not committed.

## Streamlit Community Cloud
- [ ] https://share.streamlit.io/ → Create app → existing app → select repo, `main`, `app.py`.
- [ ] In Advanced Settings, choose Python 3.12, if selectable.
- [ ] Do not put any secrets in GitHub; use Cloud app secrets configuration if required.
- [ ] Wait for build and inspect **Manage app → Logs** if errors appear.
- [ ] Confirm app's visibility is Public.

## Live browser smoke test
- [ ] Home and IPL League Explorer render.
- [ ] CSK / MI / RCB / GT / LSG franchise pages load; verify remaining five franchises too.
- [ ] Squad 2026 panel displays team, with snapshot date and roster/participants distinction.
- [ ] Season filter changes cards and charts; no red Streamlit errors.
- [ ] Player Intelligence search finds KD Karthik and V Kohli.
- [ ] Chase & Score Predictions return outputs with safe inputs.
- [ ] Team DNA year-range and single-season filters work.
- [ ] Fan Wars page displays charts and 19 fact-checked debates.
- [ ] Analyst Report Studio creates a downloadable PDF and evidence ZIP.
- [ ] Chart fullscreen controls and team logos render.
- [ ] Open the link in a private/incognito browser window that isn't logged in.

## Frequent errors
- **ModuleNotFoundError**: verify `requirements.txt` at root and redeploy.
- **FileNotFoundError**: verify project `data/`, `reports/`, `assets/` directory contents are in GitHub (folder names case-sensitive on Linux).
- **App exceeds memory limits**: reduce cache size / avoid loading large raw tables on every interaction. Use Streamlit Cloud logs to identify problem.
- **App is asleep**: Streamlit can hibernate inactive apps; opening the link wakes it.
- **Build works locally but not in Cloud**: pin the same Python/dependencies and check Windows-vs-Linux filesystem path case.
