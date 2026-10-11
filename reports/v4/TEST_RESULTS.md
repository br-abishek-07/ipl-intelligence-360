# V4 release testing results

- V3-F application base, full analytics and four deployed portable models preserved.
- **241/241 non-smoke regression tests passed** (`python -m pytest -q tests -k "not smoke"`).
- **2/2 selected smoke tests passed** (`test_v3f_page_smoke.py` and `test_v3d_pages_smoke.py`).
- **3 additional smoke tests not executed** in this V4 run. The existing V3-F history includes prior simulated page-render testing.
- **Read-only V4 preflight passed**: expected files, matched frozen data/model SHA-256, Python syntax, match IDs and winner IDs, source archive CRC, coaching metadata presence, basic credential scan.
- **8-page PDF report visually rendered; 19-slide PowerPoint visually reviewed**. This doesn't guarantee rendering parity with your Windows font environment.
- **Actual Streamlit browser and cloud deployment remain unverified.** A live URL is not included.

## Avoid overstating these checks
Passing unit tests does not prove the visual browser layout works, guarantee fixed forecast accuracy on future matches, or establish causal coaching/player relationships.
