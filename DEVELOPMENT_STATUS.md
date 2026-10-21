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
