# Viva — Targeted Questions and Answers

**Why this dataset?** Cricsheet offers event-level match JSON with stable player IDs, outcomes, and balls, enabling reconstructable innings/player calculations.

**Why normalize historical team names?** Franchise renames can split metrics. We track current identities and keep genuinely discontinued franchises separate.

**What is a legal ball?** A delivery that counts toward over completion, distinguishing wides/no-balls as required. Run rate and phase stats must be denominator-consistent.

**Why exclude Super Overs?** They are tie-break procedures, not ordinary regulation innings; counting them inflates player and team run/wicket rates. Their final result *does* affect match win classification where a winner exists.

**Can you compare franchise win rates across all years?** Carefully: teams entered in different seasons and faced changing opposition and rules. Use matched-season filters; do not claim causal ranking.

**What is a Brier score?** The average squared error between a predicted probability and a binary outcome; smaller is better. A 90% classification rate does not automatically imply well-calibrated probabilities.

**Why a 70% accuracy requirement?** User-facing classification must clear a measurable gate AND beat trivial baselines. An imbalanced always-no-wicket model might be 85% accurate but useless.

**Are your four models actually validated on fresh 2027 IPL matches?** No. The reported 2025–2026 records were reused in iterative development, so these remain retrospective research candidates.

**Does Team DNA predict wins?** No. It summarizes historical relative standing under sample constraints. Its percentiles are not probabilities or causal tactical effects.

**What if an examiner asks about live data?** The current app supports manual game states only and lacks automatic real-time score ingestion.

**Best captain rankings?** Unavailable until sourced captain-by-match identity data can be verified; the project intentionally avoids invented rankings.

**What is the greatest improvement you would make?** Obtain independently verified 2027 data, complete captaincy/availability datasets, and assess calibration/drift on untouched future seasons.
