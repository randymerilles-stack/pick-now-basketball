# Pick Now basketball

Standalone live-data validation app. Existing basketball-handicap-analyzer is untouched.

## Run and verify

Python 3.11+; no dependencies. Run `python -m unittest -v`, then `python app.py`. Render build: `python -m unittest -v`; start: `python app.py`. Bind: 0.0.0.0 and Render's PORT. `/health` reports app availability, not odds validity. `/api/pick-now` fetches a fresh snapshot. GET and HEAD supported for the home and health paths.

## Full Game line checks

The provider documents live basketball Game as group 112 (pregame 1453). Quotes must be Game / Line, in-play, with no period qualifier. Require consistent sport/fixture/team/selection identities, exactly two opposite lines in the same market, finite decimal prices above 1, non-suspended selections, timezone-aware timestamps and fixture polled_at within 30 seconds of provider server_time. Provider server_time must be within 60 seconds of our request clock. Stable prices are not rejected solely for old ts. Quarter, half, winner, virtual basketball, duplicate fixtures, malformed prices, stale/future/missing polls and incomplete pairs fail closed.

Data-checked quote pairs are displayed as reference prices, not picks. Their exact event rules and prices have not been independently cross-checked with bet365 or the user's bookmaker. General bet365 AU basketball rules were reviewed: in-play Game bets include overtime; two-way markets can push. Neither this review nor unit tests prove predictive accuracy.

## Model research

`audited_fixtures.json` summarizes the initial history/closing endpoint audit. `calibration_sample.json` contains one matched, same-timestamp two-sided half-point line per fixture with a final cover label. Never treat price ticks or two sides as independent games. `calibration.py` evaluates an odds-calibration research approach with a chronological split and purges training games whose recorded outcome availability (the later of finished_at and updated_at) was after the first test decision. Run `python calibration.py` to regenerate the research report.

The 200 training / 100 held-out fixture minimum is a project research gate, not a guarantee of adequate statistical power. Even above it, the experiment stays research-only: pooled Brier score cannot establish per-league calibration, actionable edge or reliable profit. Approved betting picks remain disabled. A separate opt-in-by-owner experimental paper mode publishes unvalidated estimates for simulation only. No historical score/clock timeline was present in the audited price points, so those records alone cannot train a score/time model.

## Sources

- https://moviodds.com/doc
- https://moviodds.com/bet365-nba-odds-api/
- https://help.bet365.com.au/s/en-au/sportsrules/basketball

No bookmaker credentials, wagering, slip automation or fabricated probabilities.

## Current research result

Audit period: 13–19 Oct 2026 UTC. 357 matched fixtures; 221 training, 108 held-out, 28 overlapping outcomes purged. Market Brier: 0.249937; research model: 0.249047. The exploratory improvement interval includes zero. No reliable edge or per-league approval was established. `model_report.json` and `audit_coverage.json` retain the audit summary. Research-only; no picks enabled.

## Owner access

All pages and data APIs require an owner session. Set PICKNOW_PASSWORD_HASH to a 16-byte-or-longer hexadecimal salt, a dollar separator and the hexadecimal PBKDF2-HMAC-SHA256 digest (200,000 iterations). Set PICKNOW_ORIGIN to the exact HTTPS origin. Missing configuration fails closed. Only /health is public and returns minimal availability. Sessions expire after eight hours or restart; SIGN OUT revokes the session. Keep the password and its salted hash out of git.

## Web acceptance test

1. Open the HTTPS app in a fresh private browser window. Dashboard redirects to /login; /api/pick-now returns 401.
2. Sign in with the owner password. Incorrect passwords must not open the dashboard. The browser login uses same-origin referrer policy; foreign, null and missing request origins are rejected.
3. Open the dashboard for an automatic check, or tap REFRESH PICKS. Inspect the checked time, fixture list, reference line pairs, validation rejections and model report. Zero approved picks is expected.
4. Leave an odds snapshot for 30 seconds or switch tabs and return later. Expired prices must disappear and the app must ask for a fresh check.
5. Disconnect the network and check again. Current prices clear and the app explains the failure. Reconnect and retry manually.
6. Test on a phone: readable tables, usable CHECK LIVE DATA and SIGN OUT buttons, no horizontal page overflow.
7. SIGN OUT. Revisiting the API with the revoked session must return 401.

Run all server checks with `python -m unittest -v`. No external feed is needed for these regression tests. Live feed access is checked separately and can vary between snapshots.

## Limits of this web release

This is a private web dashboard for validation and research, not an Android APK and not an approved pick engine. The source repo is currently public; deployment uses its public Git URL and requires manual deploys. Do not commit credentials. Only a salted password hash is kept in the service environment. Sessions reset during deployments and restarts. Live data is a manually requested third-party snapshot, not a continuous direct bookmaker connection. A passing software test does not validate the model's predictive performance.

## Experimental paper forecasts (v0.5)

The owner requested paper selections using the existing research model. `paper_model.py` applies the stored regularized home logit offset to the two-sided de-vigged market probability. It does not use score/clock, injury or team-strength features. The coefficient comes from the existing 221-training/108-held-out experiment; its improvement interval includes zero. These are unvalidated model estimates, not measured confidence or approved betting probabilities.

Only current data-checked half-point Full Game Line pairs qualify, because the research target did not model pushes. One side with the highest estimated EV per fixture is selected for simulation (up to three fixtures), even if that EV is negative; negative EV is explicitly shown. EV is computed as model probability times reference decimal odds minus one, and depends on an unvalidated estimate. No staking or wager placement is supported. Reference odds and settlement are still not independently bookmaker-verified.

API `paper_picks` is separate from `picks`, which remains empty. Each paper selection is labelled not approved for betting and not independently verified. Stale/failed checks clear selections. No continuous learning, automatic result settlement or durable performance journal is enabled by this release. Paper results require a separate future evaluation; displaying selections does not establish an edge.

## Suggestion-first flow (v0.6)

Opening/reloading the authenticated dashboard automatically fetches one current snapshot. Returning to the tab or reconnecting also refreshes; concurrent requests are suppressed. Paper selections appear before collapsed reference data/model diagnostics. REFRESH PICKS manually requests another snapshot. No continuous timer polling is enabled. Missing/stale data still produces no suggestion, and approved betting picks remain disabled.

## Direct pick display (v0.7)

Team and signed handicap line are the first result, followed by matchup, odds and a short EV label. Reference/source panels and model diagnostics are not displayed on the main screen. PAPER ONLY and negative-EV labels remain visible. Validation and authentication gates are unchanged.
