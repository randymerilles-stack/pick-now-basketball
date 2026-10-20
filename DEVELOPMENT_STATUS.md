# Pick Now development checkpoint

Current release: v0.7. Experimental paper selections use market-probability calibration, not live score/time. Approved betting picks remain disabled.

Next: verify explicit quarter/period, clock semantics, league regulation lengths and contemporaneous score plus Full Game Handicap odds. Never infer quarter from score or clock alone. Collect synchronized observations and outcomes, then test score/time features out of sample. Reevaluate both teams on each refresh.

Preserve owner authentication, simple team/line/odds display, PAPER ONLY labels and stale-data rejection. Do not modify basketball-handicap-analyzer. Never commit secrets. Save evidence, tests, completed work and next steps after each run. Stop scheduled development when integration and acceptance tests are complete; report concrete access/data blockers without claiming progress.

## Priority Pick requirement

v0.8 adds Priority Pick as the main option, currently unavailable. Implement qualification using verified synchronized live performance/score, explicit period and remaining regulation time, Full Game Handicap odds, and a tested model. Evaluate timing windows out of sample, not an arbitrary quarter or guaranteed final result. Refresh must reevaluate both teams and clear/revoke stale or unqualified selections. Keep ordinary odds-calibration paper picks separate; never promote them to Priority Pick merely by EV ranking. Show team and line first when qualified, with odds and short timing rationale; PAPER ONLY until full independent odds/model validation. Until then display 'Wala pang qualified Priority Pick.'

## Language preference (v0.9)

The authenticated dashboard now has a Filipino/English selector at the top. Preference is stored locally per browser/WebView, with Filipino default and graceful storage failure. Dynamic visible result labels are translated via an idempotent text-node observer; preserve this behavior in future UI changes and provide both translations for new states. Existing APK loads this server UI. Translation checks and all 30 server regression tests passed; no physical phone verification was performed.

## Live-state audit — 20 October 2026, 19:35 Perth

Fresh source snapshot server_time 2026-10-20T11:35:37.300158126Z: 11 fixtures, all 11 with structural score/clock values, zero with explicit period. See live_state_audit.json. Added live_state.py and integrated readiness diagnostics into prospective_capture.py. Unknown clock semantics, score/clock/quote alignment and unvalidated score/time model always block priority readiness; never derive total remaining seconds or a quarter from score/clock. 16 tests passed (live-state, market validation and prospective capture); no predictive performance claim. These research-only changes are saved in GitHub; no runtime deployment needed because dashboard/backend decision code unchanged. Next: audit documented alternative explicit-period data sources and exact event alignment, then obtain synchronized historical/outcome samples. This missing period is a data-source research task, not currently a user setup action. Priority Pick remains unavailable and approved betting outputs disabled.

## Opt-in stats discovery — 20 October 2026, 20:37 Perth

Correction to prior field audit: the default response lacks a top-level period, but official https://moviodds.com/doc section 10 documents stats=1, stats.sport=basketball and stats.period. Two bounded live requests succeeded without credentials or new subscriptions. Snapshot 2026-10-20T12:37:00.104511838Z contained 14 fixtures, 10 with real-basketball stats and explicit period; 6 stats scores matched the scoreboard, 5 stats update timestamps were within 30 seconds, and 9 market pairs passed existing capture checks (different denominators; not 9 qualified score/time records). See stats_source_audit.json and reproducible audit_stats_feed.py.

Research collector now requests stats=1, preserves raw stats and explicit observed period, and emits schema_version=2 plus consistency/timestamp diagnostics. live_state.py rejects conflicting periods and non-basketball nested stats; no score/clock quarter inference. 20 tests passed (live-state, quote validation, prospective capture), including nested period capture, mismatched scores, stale/future/naive timestamps and malformed fields. Priority readiness is still always false; no probability or total game time inferred. No app.py, dashboard, authentication or betting gate changes; no runtime deployment required for this research-only change.

Next: document clock direction/ref/updated_at semantics and league-specific regulation/overtime lengths before computing remaining game time. Collect synchronized stats/clock/quotes observations and final outcome labels with durable storage, separate independent fixtures for chronological training/testing and evaluate timing windows out of sample. Stats updated_at might be a last-change timestamp, so its conservative 30s check is a diagnostic, not established freshness semantics. No external account/key is currently needed to continue this research; keep automation active. Alternative keyed sources reviewed but not activated: live-basketball-api.com and Highlightly; their clock precision/semantics and coverage remain unverified.

## Clock-transition evidence — 20 October 2026, 21:40 Perth

Added clock_audit.py: two bounded read-only snapshots, joins exact fixture ID plus home/away/league and real-basketball stats, compares clock only within the same explicit period, preserves captures and refuses to extrapolate countdown or game time. Exclusive output creation protects prior evidence. Five new tests cover clock direction, period transitions, conflicting periods, identity changes, virtual fixtures, malformed clock and mutation; 25 relevant tests passed overall.

Actual captures received at 2026-10-20T13:40:16.194349Z and 13:40:19.417076Z are saved in research_observations/2026-10-20T1340-clock.json. Three real fixtures paired, all unchanged clocks; no direction conclusion. Two market pairs per capture, four observation rows total, not four independent games. No final outcomes or validated training labels yet. All priority/approved flags remain false. OpenAPI inspected at https://moviodds.com/openapi.json did not expose a clock schema defining direction/ref semantics; do not infer guarantees from the unchanging observations. Current model/UI/backend are unchanged, so no runtime deployment for this research tool.

Next: repeat bounded transition capture across active clock movement, audit stats/score/clock consistency and establish source clock/timestamp semantics; verify league rule configurations before any remaining-time transform. Add conservative final-outcome joining with event identity and chronological availability checks, then a fixture-grouped training/evaluation pipeline. Evidence snapshots are public sports research only; never add credentials or personal data. No new paid service or user action needed. Avoid collecting indefinitely without evaluating data sufficiency.

## Language default update — 20 October 2026, 22:30 Perth

Owner requested English every login. Dashboard now initializes English on every page load and ignores previously saved localStorage language; manual Filipino/English switching still works until the page is reloaded. This supersedes the persisted-Filipino-default behavior above. Node behavior checks passed for English initialization with old saved Filipino, manual switch, and reset on new load. Preserve this default in later UI changes.
