# IPL Intelligence 360° — V2-E Records & Visual Accessibility

## Scope completed

- Added a separate **Records & Legends** page with season and franchise filters, historical championship trophies, Player-of-the-Match awards, batting milestones, bowling records and evidence definitions.
- Added **Player-of-the-Match Awards** to every existing franchise desk, derived from *the same selected match IDs* as its other KPI cards.
- Replaced disparate chart rendering with a single `dashboard/chart_ui.py` component. Every Plotly chart has a descriptive visible heading, an explicit **⛶ Full screen** button, and interactive Plotly controls. The expanded dialog includes a self-contained offline HTML download that can occupy a browser tab.
- Strengthened titles on league EDA charts, particularly for innings eligibility, run-rate units, win-rate samples and innings roles.
- Preserved the V2-D portable JSON prediction models, corrected CSK logo URL and existing ten franchise pages.

## Provenance and known limits

- Source: the user's supplied Cricsheet IPL JSON ZIP (2008–2026), identical byte-for-byte to the previous corrected project.
- 1,243 match files are recognized, with 1,234 explicit Player-of-the-Match entries; 9 matches have no award. All 1,234 extracted award identities and team appearances were resolved from per-match people registries; there are no name-only merges.
- Player fifties are individual 50–99 run match performances; centuries are 100+ run performances. Bowling 4-for and 5-for are single-match credited wicket counts, not estimated dismissals. Those counts are based on the provided ball-by-ball source.
- Championship totals use IPL final match outcomes and reflect current franchise team continuities in the project mapping. Defunct title-winning franchises are not silently merged into current teams.
- **Captaincy statistics are NOT falsely inferred.** Cricsheet match `players` lists are not captain records. `data/metadata/captaincy_match_registry_template.csv` describes the scorecard-sourced captain data needed; a verified registry can be loaded later.
- Player photos and league/team trademark images are not bundled; prior local illustrated brand marks and IPL-hosted remote team logos are retained with fallbacks.
- The source is a static historical archive, not a live feed. Future-year results require verification against authoritative external sources before published as public factual claims.

## Viewing a chart full-screen

1. Locate a named visualization on the League EDA, franchise, Comparison, Records & Legends, or home page.
2. Click its **⛶ Full screen** button. A large, interactive overlay opens. You can pan/zoom and save a chart PNG from the Plotly toolbar.
3. Use **Download interactive full-screen HTML** in the overlay and open the file in any modern browser for full-window/offline use.
4. The same component and behavior will be reused in future V2-F/G/H stages.

`Streamlit` is unavailable in the build container, so full browser rendering and visual alignment still require a Windows laptop smoke test. Chart content, event keys and output HTML are testable offline using the supplied Python tests. 
