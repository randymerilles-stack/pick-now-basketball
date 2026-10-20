# Pick Now basketball

Standalone live-data validation app. Existing basketball-handicap-analyzer is untouched.

## Run and verify

Python 3.11+; no dependencies. Run `python -m unittest -v`, then `python app.py`. Render build: `python -m unittest -v`; start: `python app.py`. Bind: 0.0.0.0 and Render's PORT. `/health` reports app availability, not odds validity. `/api/pick-now` fetches a fresh snapshot. GET and HEAD supported for the home and health paths.

## Full Game line checks

The provider documents live basketball Game as group 112 (pregame 1453). Quotes must be Game / Line, in-play, with no period qualifier. Require consistent sport/fixture/team/selection identities, exactly two opposite lines in the same market, finite decimal prices above 1, non-suspended selections, timezone-aware timestamps and fixture polled_at within 30 seconds of provider server_time. Provider server_time must be within 60 seconds of our request clock. Stable prices are not rejected solely for old ts. Quarter, half, winner, virtual basketball, duplicate fixtures, malformed prices, stale/future/missing polls and incomplete pairs fail closed.

Data-checked quote pairs are displayed as reference prices, not picks. Their exact event rules and prices have not been independently cross-checked with bet365 or the user's bookmaker. General bet365 AU basketball rules were reviewed: in-play Game bets include overtime; two-way markets can push. Neither this review nor unit tests prove predictive accuracy.

## Model research

`audited_fixtures.json` summarizes the initial history/closing endpoint audit. `calibration_sample.json` contains one matched, same-timestamp two-sided half-point line per fixture with a final cover label. Never treat price ticks or two sides as independent games. `calibration.py` evaluates an odds-calibration research approach with a chronological split and purges training games whose recorded outcome availability (the later of finished_at and updated_at) was after the first test decision. Run `python calibration.py` to regenerate the research report.

The 200 training / 100 held-out fixture minimum is a project research gate, not a guarantee of adequate statistical power. Even above it, the experiment stays research-only: pooled Brier score cannot establish per-league calibration, actionable edge or reliable profit. The live app never publishes model probabilities or picks. No historical score/clock timeline was present in the audited price points, so those records alone cannot train a score/time model.

## Sources

- https://moviodds.com/doc
- https://moviodds.com/bet365-nba-odds-api/
- https://help.bet365.com.au/s/en-au/sportsrules/basketball

No bookmaker credentials, wagering, slip automation or fabricated probabilities.

## Current research result

Audit period: 13–19 Oct 2026 UTC. 357 matched fixtures; 221 training, 108 held-out, 28 overlapping outcomes purged. Market Brier: 0.249937; research model: 0.249047. The exploratory improvement interval includes zero. No reliable edge or per-league approval was established. `model_report.json` and `audit_coverage.json` retain the audit summary. Research-only; no picks enabled.
