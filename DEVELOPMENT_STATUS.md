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

## Provider outcome joining — 20 October 2026, 22:40 Perth

Added outcome_join.py and bounded label_capture.py. Match exact fixture ID, home, away and league; require real basketball, unique finished result, valid non-tied final score, decision before finished_at, finished_at/updated_at no later than result receipt, timezone-aware timestamps, finite opposite handicap lines and valid prices. Preserve outcome_available_at at actual result receipt (or later known timestamp); never backdate knowledge to finished_at. Pushes remain null binary labels. Outputs always research-only, independently_verified=false, training_eligible=false and approved_for_picks=false.

Actual result requests received 2026-10-20T14:40:01.201313Z and 14:40:06.716342Z: both captured fixture identities matched finished provider records (202504371 final 107-92; 203074407 final 65-77). Four observation rows labelled across TWO independent fixtures; not four independent games and not evaluated forecasts. Full evidence: research_observations/2026-10-20T1440-outcomes.json. Seven new outcome tests plus previous checks: 32 tests passed. These labels cannot establish prediction accuracy or timing advantage. No model/UI/backend gate changes and no deployment required for offline research code.

Next: validate league-specific clock semantics and feature alignment, build one row per fixture for chronological model testing and report sample sufficiency. Need a durable bounded collection strategy for many independent finished games with contemporaneous score/time/odds, rather than counting ticks, sides or repeated snapshots as more games. Existing two games are insufficient. Continue research without enabling Priority Pick; preserve English on every login as requested.

## Dataset sufficiency and leakage audit — 20 October 2026, 23:43 Perth

Added dataset_audit.py and four tests. Counts fixture IDs once across repeated snapshots/markets/sides; rejects identity and final-score conflicts; selects earliest observation without looking at outcomes; conservatively purges training outcomes unavailable at first test decision. Cross-ID alias resolution is still unverified, so model training stays disabled. 36 relevant tests passed. Report dataset_readiness_audit.json: 14 observation rows, 7 unique fixture IDs, 2 with provider-matched final scores, 5 unlabelled; chronological diagnostic has zero train and one test, with one unavailable training outcome purged. This is a sample/data diagnostic, not an accuracy evaluation.

New captures received 2026-10-20T15:42:54.446447Z and 15:42:57.731477Z are persisted in research_observations/2026-10-20T1543-clock.json (filename is a run label; actual timestamps are inside). Six real fixtures paired, all clocks unchanged; 5 market pairs in each snapshot, spanning 5 new IDs. No clock-direction conclusion; no fabricated remaining-time or probability features. All training/priority/approved flags remain false. Offline research-only code/evidence; no runtime deployment needed. Preserve English default and existing owner authentication.

Next: fetch final results for the 5 pending IDs via label_capture.py using the new capture, then rerun dataset_audit.py with all capture and outcome files. Before training, verify score/clock/quarter semantics and per-league rule configurations, resolve cross-ID event aliases, and accumulate sufficient independent finished games. Consider active-play observations separated enough to see clock movement; two rapid unchanged responses do not prove synchronization. Keep collection bounded and evaluate coverage rather than accumulating duplicate ticks. No user setup or new paid service currently required.

## Temporary execution outage — 21 October 2026, 00:35 Perth

GitHub reads succeeded and checkpoint/capture remain available. The execution tool returned 'No usable execution environment is available. Wait for an environment to become available before using this tool.' The selected environment is marked unavailable. No code was modified, no tests ran, no live results were fetched and no model/deployment progress is claimed. Read-only web retrieval of the five documented result URLs was also unavailable through the search tool; no outcomes were inferred or labelled.

Pending IDs from persisted capture: 202503180, 202503183, 203224748, 202561162, 203094590. Resume label_capture.py against research_observations/2026-10-20T1543-clock.json when execution returns, then rerun dataset_audit.py with prior evidence. Last verified sample remains seven fixture IDs, two provider-labelled games and 36 passing tests from the previous run. Treat this as transient infrastructure unavailability; automation remains enabled, no user credentials/setup changes requested, and all Priority Pick and betting validation gates remain unchanged.


## Pending outcome recovery — 21 October 2026, 06:37 Perth

Execution access recovered. Bounded result requests for all five pending fixture IDs succeeded between 2026-10-20T22:36:54Z and 22:37:06Z. Exact provider outcomes and actual receipt timestamps are preserved in `research_observations/2026-10-21T0635-outcomes.json`; all 10 opposing-side observation rows were labelled across five independent games. These are provider-matched research labels only: independently_verified=false, training_eligible=false and approved_for_picks=false.

The refreshed audit `dataset_readiness_audit_2026-10-21T0635.json` now counts 14 observation rows, seven unique fixture IDs and seven provider-labelled independent fixtures, with zero unlabelled fixtures, identity conflicts or outcome conflicts. The leakage-controlled chronological diagnostic yields two training fixtures and three test fixtures; two earlier candidate training outcomes were purged because their results were not available before the first test decision. This is still far below a defensible score/time timing-window evaluation and is not a model accuracy or win-rate claim.

All 36 relevant unit tests passed after the new labels and audit. No app/model/pick gate changed and no Render deployment is required for this research-only checkpoint. Priority Pick remains unavailable. Next: independently verify clock direction and league regulation/period semantics, obtain more independent synchronized games across timing windows, resolve cross-ID aliases, and predefine a fixture-grouped chronological evaluation before fitting any score/time model.


## Additional bounded live capture — 21 October 2026, 07:42 Perth

Saved `research_observations/2026-10-21T0742-clock.json` from two actual reads received at 2026-10-20T23:42:51.577799Z and 23:42:54.913831Z. Seven real-basketball fixtures had exact ID/team/league matches, explicit periods and contemporaneous Full Game Handicap pairs in both reads; all seven fixture IDs are new relative to the prior seven-game dataset. The covered leagues are Uruguay Liga, Brazil NBB, Chile LNB, NBA, NCAAB Pre Season and Colombia Liga.

All seven clocks and scores were unchanged during the approximately 3.3-second comparison, so this capture adds independent outcome candidates but does not establish clock direction, clock reference semantics or remaining regulation time. Fourteen market observation rows represent seven independent games, not 14 games. All capture and approved-pick flags remain false. The same 36 tests passed after capture; no model/UI/backend gate changed and no deployment was needed.

Next: fetch final outcomes after these games finish, rerun the fixture-level audit across all 14 unique IDs, and add observations separated enough to capture active clock movement without turning collection into unbounded polling. Priority Pick remains unavailable until clock/rule semantics and a sufficiently powered out-of-sample timing model are validated.


## Partial result matching — 21 October 2026, 08:42 Perth

A bounded outcome check covered all seven IDs from the 07:42 capture. Two independent games are now provider-labelled: fixture 202925875 finished 77-66 and fixture 202615968 finished 66-78. The other five result queries returned no finished result and remain explicitly unlabelled; none were inferred. Full responses and actual receipt timestamps are saved in `research_observations/2026-10-21T0842-outcomes.json`.

The updated `dataset_readiness_audit_2026-10-21T0842.json` counts 28 market observation rows, 14 unique fixtures, nine provider-labelled independent fixtures and five unlabelled fixtures, with zero invalid observations, identity conflicts or outcome conflicts. The chronological diagnostic still has only two eligible training fixtures and three test fixtures after purging four outcomes unavailable at the test cutoff. All 36 tests passed.

This remains a data-readiness check, not an accuracy result. No score/time model was trained, no timing window qualified, and all Priority Pick and approved betting gates remain false. Next: retry only the five unfinished IDs after completion, then continue bounded clock-transition evidence and league-rule verification.


## Outcome checkpoint — 21 October 2026, 09:36 Perth

Saved actual bounded provider responses and receipt times in research_observations/2026-10-21T0936-outcomes.json. Three additional independent fixtures now have matched finished results. Refreshed dataset_readiness_audit_2026-10-21T0936.json counts 14 unique IDs, 12 provider-labelled fixtures and two unlabelled, with zero identity/outcome conflicts. Chronological diagnostic: seven training candidates, four test candidates and one outcome purged for late availability. These counts do not establish sample adequacy or model effectiveness. All 36 software tests passed; no forecasts were evaluated and all training/approved flags remain false.

Next: complete the remaining result joins, then prioritize clock semantics and predefined evaluation design over repetitive collection reports. Owner requested meaningful model-testing updates; suppress routine data-count notifications unless action is needed or a material blocker changes. No runtime code or deployment changed.


## Evaluation design — 21 October 2026, 10:36 Perth

Saved PRIORITY_EVALUATION_PROTOCOL.md before model fitting: exact handicap-cover target, both-side scoring, event-grouped chronological splits, causal outcome availability, frozen pre-result forecasts, market-only baseline, validation-only timing selection, untouched final testing, uncertainty and independent replication. Current live_state.py was checked against GitHub and still blocks unverified clock semantics. No model qualification or deployment occurred.

Recomputed the illustrative independent binary precision figures: ceil(1.96^2 * .25 / .05^2)=385 and the corresponding .03 figure=1068. These are explicitly not model-training minimums or a Brier-effect power analysis. No software changed, so prior 36 test results were not rerun or relabelled as new predictive evidence. Next: establish clock/rule semantics and eligible feature records, then implement grouped evaluation/forecast persistence and a development-only power analysis. Routine progress notifications remain suppressed pending model results or actionable blockers.


## Timing-window implementation — 21 October 2026, 11:42 Perth

Added offline timing_windows.py implementing the protocol's four nonoverlapping normalized regulation-time intervals. Unverified semantics, overtime, invalid/nonfinite values, bools, negative time and time beyond regulation return no window. The verification argument is a caller precondition, not independent source verification; current capture inputs remain ineligible. The helper is not connected to live app selection.

Four focused tests passed for all boundaries, distinct regulation lengths, invalid values, unknown semantics and overtime rejection. No prediction accuracy was measured; no model was trained or deployed. Next: establish documented clock/league semantics, then implement eligible feature records and chronological forecast evaluation. Priority Pick remains unavailable.


## Owner session convenience — 21 October 2026

Owner requested fewer password entries. Session and Secure/HttpOnly/SameSite cookie lifetime extended from eight hours to 30 days. Raw passwords are not stored on device. Existing server-memory session storage remains: logout, process restart/deploy or cleared cookies require login again. Eight authentication tests and all 31 local server/model regression tests passed, including next-day authentication, exact 30-day expiry and logout revocation. Release commit 4a2a9750b68efb95a837cdb9d264ea6529c9cc41 sent to Render; inspect deployment before any redeploy. No model gates changed.


## Result checkpoint — 21 October 2026, 12:34 Perth

Saved research_observations/2026-10-21T1234-outcomes.json with actual response receipt times. One additional NBA fixture is now provider-labelled. Aggregate dataset_readiness_audit_2026-10-21T1234.json reports 14 unique IDs, 13 provider-labelled games and one unlabelled, zero invalid rows or identity/outcome conflicts. Chronological diagnostic: seven train candidates, four test candidates, two late-availability outcomes purged. Eleven focused outcome and dataset tests passed. No model fitted, forecast evaluated, source semantics verified or betting gates enabled.

Next: investigate the remaining unlabelled fixture and prioritize documented source clock/period semantics; do not confuse counts with model validation. No runtime deployment needed. Preserve the newly released 30-day session setting and English default.


## Source semantics re-audit — 21 October 2026, 13:33 Perth

Fresh official documentation review saved in SOURCE_SEMANTICS_AUDIT_2026-10-21.md. Clock direction/ref semantics still absent. Identified an actionable validation gap: fixture polled_at does not prove the selected handicap group was read recently; documented group_status provides market-specific confirmation. Existing validation.py has no group_status check. Prior data_checked counts must not be interpreted as verified contemporary group odds.

Next run should prioritize implementing and testing exact-group freshness rejection, including fresh-fixture/stale-handicap regression, then safely deploy/verify paper-feed validation. No code changed or tests rerun in this documentation audit, no picks/model enabled. Results remain provider-only labels; forecast effectiveness is untested.


## Handicap group freshness — 21 October 2026, 14:36 Perth

validation.py now requires group_status['112'] with a recent timezone-aware polled_at and no stale/invalid flag, independently of fixture freshness. Missing/wrong-group/malformed/old/future group confirmation fails closed. Added regression for fresh fixture plus stale handicap group and retained stable-price timestamp behavior. All 41 local research tests passed, including the new regression; no prediction effectiveness inferred.

Committed release 6ed07f1eb7257b00c0104e997e8891f299a134dc; manual Render deployment requested after confirming no new automatic deployment. Check actual deployment status before further release actions. Approved picks/score-time model remain disabled; 30-day owner session and English default preserved. Next: verify live release and current-feed coverage under the stricter check, then establish source clock/rule semantics. Earlier capture datasets lack this stricter provenance and must not be treated as validated odds records.


## Strict-check live coverage — 21 October 2026, 15:41 Perth

Confirmed Render release 6ed07f1eb7257b00c0104e997e8891f299a134dc is live, deployed at 2026-10-21T06:38:46Z. No duplicate deployment requested. Two bounded current-feed reads received 07:41:45.697658Z and 07:41:48.580525Z passed one Full Game Handicap pair each under the new exact-group freshness check. Evidence: research_observations/2026-10-21T1541-clock.json. One new fixture ID 203192934 (Philippines UAAP), explicit period 3, unchanged clock 10:00 with ticking=false and ref=07:33:39Z. No countdown/ref/remaining-time conclusion is justified.

Nineteen focused validation/capture/clock tests passed. This is real-feed coverage evidence, not prediction validation. All priority/approved flags remain false. Collector currently records the source digest and validation result but does not preserve raw group_status in each observation; add that provenance before treating future research captures as independently re-auditable group freshness evidence. Next: preserve selected-group raw confirmation and compare suitably separated live observations; establish documented clock semantics and league rules before model features.


## Capture provenance — 21 October 2026, 16:34 Perth

Research capture schema v3 now preserves handicap_group_id=112 and a detached raw handicap_group_status_observed record for every accepted observation. This permits later review of selected-group polling time and flags without confusing fixture freshness with market freshness. Earlier schema v2 records were not backfilled or promoted. Fifteen focused capture/validation tests passed, including input-mutation independence and existing stale/wrong-group rejection tests. No runtime app change/deployment required, no training or approved outputs enabled.

Next: obtain schema v3 observations across active clock movement, establish clock/league semantics and build eligible feature records before forecast evaluation. Raw provider provenance remains distinct from independent odds verification.


## Spaced clock movement — 21 October 2026, 17:39 Perth

Added bounded --interval-seconds (0..30) to clock_audit.py. Actual schema v3 observations received 09:38:52.920962Z and 09:39:16.288232Z are saved in research_observations/2026-10-21T1738-clock.json. Three exact-identity real fixtures with explicit periods and three paired handicap markets per capture: Australia NBL 202562243 Q3 clock decreased 395 to 381 seconds; Club Friendlies 203169631 period 2 decreased 436 to 413; PBA 202560895 period 2 unchanged at 720. Raw selected-group freshness provenance is retained.

This is the first observed same-period countdown movement in collected evidence, not general verification of source reference semantics or synchronized timestamps. Different ref/clock deltas remain unexplained; no remaining-time feature inferred. Nine focused clock/capture tests passed. All semantics_verified/priority/approved flags remain false; research-only tool, no deployment required. Next: inspect documented league rules and source clock ref/ticking behavior, gather independently aligned state evidence, and evaluate eligible feature coverage before fitting a model.


## Schema v3 outcome matching — 21 October 2026, 18:41 Perth

Bounded final-result queries for the three spaced schema v3 captures completed and are saved with actual receipt times in research_observations/2026-10-21T1841-outcomes.json. Four repeated observation rows across two independent fixtures matched provider finished results; one fixture remains unlabelled. Seven outcome-validation tests passed. These are research-only labels with training_eligible=false and approved_for_picks=false. No forecasts were scored and no effectiveness claim is supported.

Next: investigate documented NBL/other league regulation rules and clock ref/ticking semantics; capture provenance alone cannot establish synchronized state or independently verified odds. Retry remaining outcomes when available; retain all prior receipts without backdating knowledge. No runtime change or deployment.


## Primary duration-rule evidence — 21 October 2026, 19:40 Perth

Reviewed official FIBA 2026 v1.1 rules, articles 8.1 and 8.7 (four 10-minute regulation periods and five-minute overtimes), and NBL's 3 September 2026 announcement of FIBA rule changes for 2026-27. Saved league_rule_evidence_fiba_2026.json with exact primary URLs, candidate duration constants and explicit mapping limits. NBL announcement is not itself an explicit duration/competition-exception confirmation. No automatic league mapping enabled.

Four timing-window tests passed; no rule transform or source clock semantics approved. This source research narrows the rule dependency but cannot validate live time alignment or predictive accuracy. Next: verify exact NBL competition duration mapping and provider clock semantics, then implement a gated remaining-time transform. Preserve abstention until these prerequisites and model evaluation are met.


## Remembered-login defect acceptance — 21 October 2026, 20:40 Perth

Owner reported another login prompt from the existing Android app. Current GitHub access.py and the actual Render release were checked: release 6ed07f1eb7257b00c0104e997e8891f299a134dc is still live; no duplicate deploy requested. Cookie Max-Age is 30 days but SESSIONS is a process-local dictionary. A real two-process test confirms that a newly issued session authenticates in its original process and fails in a fresh process using the identical synthetic password configuration. This establishes a reproducible server-side defect; it does not establish whether that particular phone prompt was caused by a restart, lost WebView cookies, or logout.

Saved test_session_restart.py as a durable acceptance check. Results: one ordinary test passed and one explicitly expected failure for the unimplemented restart-persistence requirement. An expected failure is NOT a working feature or successful acceptance test. No production password, password hash or owner token was used; test credentials are synthetic. No runtime changes or deployment made.

Next: implement restart/deploy-resistant authentication while retaining expiration, tamper rejection, logout revocation and password-change revocation; verify Android WebView cookie persistence as a separate acceptance requirement. Do not merely lengthen Max-Age again or persist session secrets in the public repository. Before choosing signed cookies, resolve durable logout revocation: clearing the browser cookie alone must not silently replace the existing server-side revocation guarantee. Storage/key configuration must survive replacement instances and use no new paid service. No architecture is yet accepted or implemented.

Accepted owner targets: 22 October 2026, 18:00 Perth for the persistent-login fix and testing, and a separate Priority Pick feasibility checkpoint at the same time. These are targets, not completed work or a promised validated prediction model. Phone acceptance is still outstanding; report exact blockers and revised timing if the target cannot be met. Priority/model research requirements remain unchanged, with approved betting outputs disabled.


## Gated regulation-time arithmetic — 21 October 2026, 21:37 Perth

Added remaining_time.py, an offline helper computing observed regulation seconds only for an explicit within-period countdown with separately verified clock semantics, league rules and score/clock/quote alignment. All three verification inputs must be literal True; they are caller preconditions, not evidence or independent verification. No current provider/league mapping is approved to set these flags. No clock-ref extrapolation, inferred period, overtime horizon, live wiring, model fit or selection was added.

Four focused tests passed: distinct regulation formats, boundary arithmetic, missing/untruthful verification flags, unknown directions, overtime, ambiguous periods, malformed/nonfinite/bool inputs and impossible clocks. Synthetic arithmetic tests establish software behavior only; they do not establish current-game accuracy or prediction effectiveness. Existing live_state.py still emits remaining_regulation_seconds=None and priority_ready=False. No runtime deployment needed.

Next: establish provider per-period countdown/ref semantics and exact competition mapping, then feed independently aligned eligible states into this helper and the frozen evaluation protocol. The remembered-login defect remains open with the separately recorded 22 October 18:00 Perth target; no authentication fix was implemented in this run. Preserve its logout/password-change revocation acceptance requirements.


## Explicit alias audit — 21 October 2026, 22:40 Perth

Rechecked current provider documentation (/doc, /docs/python/, /docs/sports/). No clock.min/sec/ref definition establishing per-period countdown/ref alignment was found. Did not promote observed countdown movement to verified semantics.

Added event_aliases.py and bounded audit_event_aliases.py: accepts only an explicit, internally consistent /closing fixture_ids declaration containing the requested numeric-string ID, validates response fixture_id and optional prematch_id, and never merges by team name. Three focused tests passed for valid single/multiple aliases, missing declarations, conflicting IDs, duplicate IDs, malformed and Unicode IDs. This is provider-asserted identity evidence, not independent event verification.

Actual read-only requests for the four recent IDs (202562243, 202560895, 203169631, 203192934) all succeeded. Each endpoint declared only its requested ID; none exposed a separate prematch alias. Saved alias_evidence_2026-10-21T2240.json with actual receipt timestamps, response digests and identity field projections. The reproducible script preserves full raw parsed responses locally; durable evidence deliberately retains only relevant identity projections. Absence of an extra declared alias does not prove no alternate ID exists. No dataset grouping, model, runtime app or deployment changed.

Next: extend alias evidence to the complete candidate dataset before any grouped train/test split; keep cross-ID independence unresolved until corroborated. Source clock semantics, independent handicap verification and sufficient validated training records remain open. Login fix remains open under its separate acceptance target. All training/approved-for-picks gates remain false; no forecast effectiveness measured.


## Durable-session backend and hosting dependency — 21 October 2026, 23:39 Perth

Read current access.py and checked Render service srv-dbbd6mff3r2c738f4nsg in the confirmed workspace. It remains plan=free. Both list_postgres_instances and list_key_value returned no instances. Official https://render.com/docs/disks was read (Markdown retrieval unsupported, HTML succeeded): durable attached disks require a paid supported service; default filesystem changes are lost on restart/redeploy. No resource, plan, environment variable or deployment was changed and no paid service was created.

Prepared durable_sessions.py as a standalone SQLite backend, NOT connected to access.py. Stores only token SHA-256, credential-generation identifier and expiry; 128-session bound, transactional creation, persistent deletion for logout, literal expiry and credential-generation checks. Three meaningful tests pass, including a genuinely separate Python process authenticating the token and revoking it, a new backend instance rejecting the revoked token, exact 30-day expiry, altered credentials/tokens and capacity eviction. Synthetic temporary data only. These tests establish behavior when the same database file survives; they do not simulate Render replacement storage or Android cookie persistence.

Deployment dependency: this backend requires a real durable mount, currently unavailable on the existing free service. A free external durable session datastore is an alternative but none is connected or provisioned; that route still needs feasibility/access work and a different adapter. Do not place SQLite on Render's ephemeral filesystem and claim the login defect fixed. Do not weaken logout revocation with restart-forgotten revocation lists. Keep live access unchanged until end-to-end restart/deploy, logout, password-change and device-cookie acceptance pass.

Next: investigate a no-cost external durable store accessible through existing authorized tools, or report a concrete user setup dependency if none is available. Persistent-login target remains conditional on resolving storage; do not promise completion merely from these backend tests. Priority data/model research remains independently actionable; all approved betting outputs stay disabled.


## No-cost storage decision and access pause — 22 October 2026, 00:34 Perth

Saved PERSISTENT_LOGIN_FEASIBILITY_2026-10-22.md with current primary-source constraints and verified connection state. Free Render Postgres expires after 30 days; free Key Value lacks persistence. Neither is a durable permanent login fix. Neon has a Free plan, and an available Neon integration was found and suggested; it is not installed/connected. No new account/resource/paid service was created. A PostgreSQL adapter is still required after datastore access is confirmed; the SQLite module is not a deployed solution.

Fresh authoritative GitHub backend/tests were reread and three focused authentication-storage tests passed again. No production release, phone acceptance or model qualification occurred. The owner must install/connect Neon before the next datastore implementation/access test can proceed. Never request secrets in chat or public GitHub.

Pause the existing recurring task for this persistent user-action dependency; preserve all code and current private/PAPER ONLY app. Resume after connection confirmation, reverify Free-plan scope and Render state, implement/test the adapter and only then deploy and check restart/logout/device acceptance. Priority Pick still requires source-clock/odds verification and a sufficiently powered frozen out-of-sample evaluation; routine helper commits cannot substitute for those data prerequisites. Today's 18:00 Perth target remains unconfirmed.


## Neon access restored — 23 October 2026, 13:54 Perth

Owner confirmed installation. Successful Neon list_projects/list_organizations calls verified access; organization org-rapid-water-77081468 (randy) reports plan=free, with no pre-existing projects. Provisioned exactly one standalone pick-now-basketball project, noisy-cloud-18199235, region aws-us-west-2, compute min/max 0.25 CU. Initial request specifying suspend timeout was rejected by Free-account policy; verified no partial project before retrying without the unsupported option. Project creation then succeeded. No paid plan or unrelated app changed.

Read-only SQL SELECT current_database(), 1 succeeded against neondb. No schema, production session or connection secret has been committed. Render still runs release 6ed07f1eb7257b00c0104e997e8891f299a134dc; no deploy was requested. The Neon access blocker is resolved, but the app is not yet wired to Postgres and remembered-login remains unfixed in production.

Resume the existing scheduled development task with this checkpoint. Next priority: implement a Postgres-backed session adapter in the current Python app, preserve password authentication, server-side logout and credential-change revocation, secure cookies and expiry; test on an isolated database branch, configure the server-only pooled URL securely through Render environment merge, run required checks, inspect deploy state and verify actual live release/restart behavior. Follow the Neon Postgres/branch and Render environment skills before these operations. Never expose credentials in public GitHub, logs or chat; preserve all PAPER ONLY/model gates. Phone-cookie acceptance remains outstanding.


## Postgres adapter and isolated SQL acceptance — 23 October 2026, 14:39 Perth

Reread current GitHub access.py/app.py/auth tests before changes. Added pg_sessions.py as an unwired Postgres session backend with transactional advisory-lock capacity enforcement, token digests only, 30-day expiry, credential-generation matching and durable token deletion. Connection/SQL errors are sanitized as SessionStoreUnavailable rather than exposing DSN/driver context. Schema migration is explicit, outside request authentication. Added requirements.txt pinned psycopg[binary]==3.2.13; installed successfully in this runner.

Created one isolated test branch br-rough-rain-arlf585i (test-persistent-login-20261023), parent br-restless-frost-arbyuyng, in existing project noisy-cloud-18199235. CLI was absent; authenticated MCP used. No production session data existed or was copied. Applied CREATE TABLE only on the test branch. Saved postgres_session_acceptance.sql: actual database-side expiry-before/exact-boundary, changed-generation rejection and deletion checks completed without assertion errors in a rolled-back synthetic subtransaction. Subsequent independent query confirmed zero session rows. These SQL tests do NOT establish application transport or process-restart acceptance.

Added opt-in test_pg_sessions.py for actual Python driver and separate-process authentication/revocation. Running it with the test branch URL FAILED: runner DNS could not resolve the Neon endpoint (Temporary failure in name resolution). Connector SQL access worked. No credential was printed or committed. py_compile passed for both new Python modules. This transport failure must not be relabelled as a passing restart test; test is skipped in ordinary unittest discovery unless PICKNOW_TEST_DATABASE_URL explicitly points at an isolated test database.

access.py and app.py remain unchanged, so live login is still process-memory-only. No Render environment changes/deploy and no model gate changes. Next: test the Python driver from an environment that can resolve/reach Neon (possibly a controlled Render acceptance path), then wire the adapter with fail-closed handling for authentication/create/logout errors and test the HTTP flow before release. Configure server-only pooled production URL via authorized environment merge only when ready; schema migration uses direct URL. Keep old expected-failure memory-session test until replacement is actually accepted. Test branch retained for continuation; do not create another duplicate. No user action currently identified; continue scheduled work and recheck transient runner networking.


## Auth routing and outage acceptance — 23 October 2026, 15:42 Perth

Current source reread. access.py now uses PostgresSessions when PICKNOW_DATABASE_URL is explicitly configured; an unavailable configured store never falls back to process-memory login. A SHA-256 domain-separated fingerprint of the server-only password configuration is passed as the credential generation (raw hash/password never stored in the session table). app.py handles sanitized storage errors with HTTP 503 and Retry-After for protected GET/HEAD, sign-in and logout. Logout failure does not report success or erase the cookie before durable revocation succeeds. Without a configured DSN, existing memory mode remains.

Added test_persistent_access.py using a real temporary SQLite store injected behind the same adapter contract. Nineteen distinct HTTP/security checks passed (eight baseline plus eleven persistent variants): cookie attributes, origin rejection, throttling, 30-day expiry, memory-loss survival, password-change rejection, logout revocation, anonymous denial, configured-storage failure without fallback and 503 handling. This is backend-routing validation, not Postgres transport acceptance. Synthetic baseline tests explicitly clear PICKNOW_DATABASE_URL so future build-time testing cannot write test-password sessions to production.

Runner DNS retry still failed for the Neon endpoint with Temporary failure in name resolution. No production DSN configured, migration on main, deployment or live restart claim. Render deploy inventory before commits still showed only live release 6ed07f1eb7257b00c0104e997e8891f299a134dc. Existing public-Git service has historically required manual deploy; no trigger requested this run. Source changes are safely dormant until DSN configuration. All betting/model gates preserved.

Next: use a controlled Render build/runtime acceptance path to execute test_pg_sessions.py against existing test branch br-rough-rain-arlf585i when runner cannot reach Neon. Confirm dependency installation with current Render build command (python -m unittest -v); requirements.txt alone must not be assumed installed by that command. Use a pre-release verification script/build wrapper if needed, and run actual Postgres process-restart tests before production activation. Then migrate main via direct connection, merge pooled server-only URL securely, inspect actual deploy and verify live auth/restart/logout. No additional user action identified.


## Render acceptance gate and automatic approval blocker — 23 October 2026, 16:42 Perth

Re-read latest source/status and Render configuration. Existing buildCommand is python -m unittest -v with no package-install step, and current connector cannot update that command. Added explicit opt-in test_00_release_dependencies.py, enabled only by PICKNOW_RELEASE_ACCEPTANCE=1, to install pinned requirements before Postgres acceptance tests execute under sorted unittest discovery. Captures install output to avoid leaking index/environment context; checks psycopg 3.2.13. Focused local gate test passed. No production login claim follows from this dependency check.

Attempted a merge-only Render environment update of PICKNOW_RELEASE_ACCEPTANCE and PICKNOW_TEST_DATABASE_URL, scoped to the existing isolated test branch. Automatic approval review REJECTED it before execution. Exact stated reason: persistently uploading a Neon test-branch credential to the production Render service is a sensitive external disclosure not explicitly authorized and may grant unintended runtime access. Neither value was applied by that attempt; no deployment was triggered. Do not retry via CLI/browser/indirect execution to evade the rejection.

Render deployment inventory still contains only live 6ed07f1eb7257b00c0104e997e8891f299a134dc. Main Neon session schema is not migrated and production URL not configured. Code remains saved but live owner login is unchanged. Local runner DNS restrictions still prevent direct Postgres process acceptance; real SQL assertions on the isolated branch passed in the prior checkpoint.

User action required by automatic approval review: explicit approval to store the dedicated Neon connection credentials as server-only Render environment secrets for this integration (test branch for acceptance, dedicated production branch for live owner sessions). Never display the values, commit them, or replace unrelated environment keys. Report the disclosure boundary and obtain that specific approval before the rejected class of action is retried. Pause the existing schedule for this persistent approval dependency, rather than repeat failed updates. Once approved, reread this checkpoint, execute the controlled acceptance build, then migrate/activate production only after tests pass. All PAPER ONLY/model safeguards remain unchanged.


Release-gate verification correction: the first focused invocation failed because the scratch copy lacked requirements.txt; after fetching the authoritative requirements, pip succeeded but this already-running interpreter did not yet include the newly created user-site directory. Fixed the gate to add site.getusersitepackages() after installation. Final focused invocation passed (one test, psycopg 3.2.13), exit 0. The earlier checkpoint's passing result refers to this final corrected run; the intervening failures were setup/import issues, not successful Postgres acceptance. Automatic-approval rejection and paused schedule remain unchanged.


## Persistent login released and live redeploy acceptance — 23 October 2026, 18:39 Perth

Owner explicitly approved transferring dedicated Neon credentials into secure Render environment variables for testing and production login. Retried the previously rejected merge with that explicit authorization; it succeeded. Existing password/origin and unrelated environment keys were preserved. Credentials were never printed or committed. Test branch and production branch remain separate; no paid resource/plan was created.

Controlled Render acceptance exposed an unsupported pooled startup parameter: psycopg options='-c statement_timeout=5000'. Replaced it with SET LOCAL statement_timeout inside each transaction, retaining connect timeout and sanitized diagnostics. Initial builds failed safely and left the prior live app running. A legacy memory-subprocess test also inherited production DB configuration during the activation build; isolated it explicitly with PICKNOW_DATABASE_URL='' before the successful release. No durable owner sessions had yet been issued. A string-replacement editing error then broke that test source; replaced it with a checked local file and verified its two subprocess tests. These failed builds are not counted as successful releases.

Final source release 495afe8af650d3fdf997f57e3fb9eb26a885a773 passed all 85 Render tests with no expected failures, including real Postgres authentication from a separate process, logout revocation, expiry and changed-generation rejection. Explicit memory fallback now has an ordinary negative persistence test rather than an expected-failure marker. Main schema created through authorized Neon SQL; pooled main URL is configured as PICKNOW_DATABASE_URL. Release activation dep-dbdjfsrncjis73adqcc0 became live at 10:34:26.695552Z.

Actual owner-authorized HTTPS acceptance used the existing private owner credential without displaying it. Login succeeded, protected home and API returned 200, approved picks remained empty and paper_mode=simulation_only. Kept the exact cookie across a deliberate same-source Render redeploy dep-dbdjgrpsrm7s73bvejrg (live 10:36:38.947693Z). After the new instance was live, the saved cookie still authenticated and private API returned 200. Logout succeeded; replaying the original cookie redirected to login. Independent production database query then showed zero remaining session rows. Temporary acceptance cookie file was removed. See SESSION_RELEASE_ACCEPTANCE_2026-10-23.json for non-secret durable evidence.

Server-side remembered login is now deployed and verified across actual replacement. Existing clients will need one fresh sign-in because earlier process-memory cookies cannot be recovered. No new APK was built or required for this server change. Physical Android close/reopen acceptance remains outstanding; do not claim it was performed. Raw passwords are not stored in the device by this change; expiry is 30 days, with logout, cleared cookies or changed password configuration requiring login again.

Resume the existing development schedule: credential-transfer authorization persists; do not ask for the same approval again. Preserve the working session backend and release gates. Next priority returns to verified synchronized score/explicit period/clock/Full Game Handicap odds and a sufficiently powered, frozen out-of-sample model/timing evaluation; Priority Pick remains unavailable and approved betting outputs disabled. Do not confuse the completed login release with model reliability. Avoid redundant deployment/testing unless code or unresolved acceptance concerns justify it.


## Cross-source live-state corroboration — 23 October 2026, 19:37 Perth

Read authoritative source/status before returning to Priority Pick data work. Added bounded read-only audit_dual_scoreboard.py and event-specific project_scoreboard_evidence.py, plus scoreboard_alignment.py. Comparison requires exact NBL home/away names, timezone-aware tip-off equality and a single ESPN competition/event identity; it never fuzzy-matches or qualifies training. Six focused tests passed for identity/orientation/date mismatches, period changes, malformed clocks, internal stats-score disagreement and persistent no-approval flags. Local validation.py blob was checked against current GitHub (92ce4dbb5b9c78e28539dd39ad6917ead62ac638) before strict handicap inspection.

Actual source reads corroborate provider fixture 202674359 (Perth Wildcats home, Melbourne United away, Australia NBL, tip-off 10:30Z) with ESPN event 401875274. First pair: provider received 11:39:13.181813Z, ESPN 11:39:15.729199Z; both scoreboard and stats 54-59, explicit period 3, but clock 6:35 versus ESPN 6:30. Receipt gap 2.547386s; 5s observed clock disagreement. Second pair: provider received 11:41:20.753933Z, ESPN 11:41:26.381165Z; provider scoreboard 56-62 while its own stats and ESPN showed 58-62. Same explicit period 3; provider clock 5:49 versus ESPN 5:45. Receipt gap 5.627232s; 4s clock disagreement. Both provider responses contained one handicap pair passing existing exact-group freshness checks, which does not establish score/clock/quote synchronization or independently verified odds.

Evidence projections saved in scoreboard_evidence_2026-10-23T1939.json and scoreboard_evidence_2026-10-23T1941.json with actual receipt times, HTTP cache metadata, full-response hashes, relevant raw state and group-112 quotes. Full raw captures remain reproducible via the bounded collector; durable projections omit unrelated fixtures/player fields. Separate websites may share upstream data; describe this as cross-source corroboration, not proof of independent event-time accuracy. Projector intentionally targets only the explicitly reviewed IDs/date, not a universal fixture mapper.

This is the first separate-scoreboard comparison in this work, and an observed counterexample to assuming a recent handicap poll gives an atomic live state. No score/time records promoted, no model trained, no forecasts evaluated or picks enabled. No runtime app/auth changes, redundant tests or Render deployment. Next: inspect ESPN event play-by-play/event-time fields and provider state updates to define a defensible alignment rule; retain both sources and rejection evidence, then obtain qualified records for the frozen evaluation protocol. Preserve the completed persistent-login release; no user action currently required.


## 2026-10-23 — play timestamp feasibility audit

Added offline `play_timestamp_audit.py` and five focused tests; 11 timestamp/alignment tests passed together. Evidence: `play_timestamp_evidence_2026-10-23T2041.json` retains source URLs, capture metadata, exact event identities and reversal examples. NBL event 401875274 has 418 plays and no play wallclocks (`wallclockAvailable=false`). NBA events 401909093 and 401909094 each have 513 valid timezone-aware wallclocks, but respectively 7 and 8 backward transitions in source order. Complete ordered coverage therefore fails for both; timestamps were not silently sorted. Retrospective receipts are retained separately and do not establish real-time availability. NBL capture only retained local file-write timing, explicitly labelled as a limitation.

No training rows, probability evaluation or Priority Pick produced. No runtime/auth changes or deployment. Working persistent login remains untouched. Next: investigate NBA timestamp reversal semantics and prospectively capture contemporaneous score/explicit period/clock plus Full Game Handicap odds, before attempting out-of-sample modelling. Independent odds verification and evaluated timing windows remain required; all outputs stay PAPER ONLY and approved picks disabled.


## 2026-10-23 — timestamp reversal interval diagnostics

Read current GitHub status and timestamp audit before work. Added offline timestamp_ambiguity.py, four tests and timestamp_ambiguity_evidence_2026-10-23.json. Reused the explicitly identified 12:43Z retrospective captures (not new live evidence). All 7 reversals in NBA 401909093 and all 8 in 401909094 have unchanged period, displayed clock and scores across the adjacent reversal; maximum backward jumps are 238s and 140s respectively. This observation does not establish why timestamps reverse, their provider semantics or real-time availability. Evidence retains every reversal interval and source capture metadata. Do not silently sort, interpolate or use these diagnostics as a historical quote join. Intervals are not a complete unsafe-join detector.

Validation: 15 timestamp/scoreboard tests pass, including changed-state detection, invalid timestamps, exact interval boundaries, input immutability and persistent no-approval flags. No app/auth change or Render deployment. No qualified training records/model/picks produced. Next actionable data step remains prospective paired score/explicit-period/clock/handicap captures and documented source timing semantics; odds independence and frozen out-of-sample timing/model evaluation still unmet. No user action required by this diagnostic step.


## 2026-10-23 — reusable prospective paired collector

Added paired_capture.py with bounded concurrent provider/NBA/NBL requests, explicit requested calendar date, actual per-source receipt and HTTP/cache/hash metadata. Durable projection retains provider raw score/clock/period/stats and group-112 quotes plus scoreboard event/competition identities and home/away scores. It never infers periods or automatically maps fixtures. Three focused tests pass (calendar validation, raw quote/state retention, partial failure remains unqualified). An initial projection used the wrong odds key; corrected to source quotes and repeated the bounded capture before saving final evidence.

paired_capture_evidence_2026-10-23T2240.json: successful provider receipt 14:40:06.383870Z, NBA 14:40:06.631946Z and NBL 14:40:06.639835Z. Provider had 18 fixtures; scoreboards 12 NBA events and 1 NBL event. These counts are coverage only, not matched live training examples. Source response SHA256 refers to full original payload; durable file is explicitly a projection. Only group112 quotes retained, not other markets. No synchronized fixture was established or record promoted. Concurrent receipt does not imply atomic source updates or independently verified odds. Next run can use the reusable collector for current coverage and exact fixture comparison rather than retrospective timestamp repair. No runtime/auth changes or deploy; model evaluation remains blocked on qualified data, Priority Pick stays unavailable, PAPER ONLY and no approved picks.
