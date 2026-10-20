# Pick Now development checkpoint

Current release: v0.7. Experimental paper selections use market-probability calibration, not live score/time. Approved betting picks remain disabled.

Next: verify explicit quarter/period, clock semantics, league regulation lengths and contemporaneous score plus Full Game Handicap odds. Never infer quarter from score or clock alone. Collect synchronized observations and outcomes, then test score/time features out of sample. Reevaluate both teams on each refresh.

Preserve owner authentication, simple team/line/odds display, PAPER ONLY labels and stale-data rejection. Do not modify basketball-handicap-analyzer. Never commit secrets. Save evidence, tests, completed work and next steps after each run. Stop scheduled development when integration and acceptance tests are complete; report concrete access/data blockers without claiming progress.

## Priority Pick requirement

v0.8 adds Priority Pick as the main option, currently unavailable. Implement qualification using verified synchronized live performance/score, explicit period and remaining regulation time, Full Game Handicap odds, and a tested model. Evaluate timing windows out of sample, not an arbitrary quarter or guaranteed final result. Refresh must reevaluate both teams and clear/revoke stale or unqualified selections. Keep ordinary odds-calibration paper picks separate; never promote them to Priority Pick merely by EV ranking. Show team and line first when qualified, with odds and short timing rationale; PAPER ONLY until full independent odds/model validation. Until then display 'Wala pang qualified Priority Pick.'

## Language preference (v0.9)

The authenticated dashboard now has a Filipino/English selector at the top. Preference is stored locally per browser/WebView, with Filipino default and graceful storage failure. Dynamic visible result labels are translated via an idempotent text-node observer; preserve this behavior in future UI changes and provide both translations for new states. Existing APK loads this server UI. Translation checks and all 30 server regression tests passed; no physical phone verification was performed.
