# Pick Now development checkpoint

Current release: v0.7. Experimental paper selections use market-probability calibration, not live score/time. Approved betting picks remain disabled.

Next: verify explicit quarter/period, clock semantics, league regulation lengths and contemporaneous score plus Full Game Handicap odds. Never infer quarter from score or clock alone. Collect synchronized observations and outcomes, then test score/time features out of sample. Reevaluate both teams on each refresh.

Preserve owner authentication, simple team/line/odds display, PAPER ONLY labels and stale-data rejection. Do not modify basketball-handicap-analyzer. Never commit secrets. Save evidence, tests, completed work and next steps after each run. Stop scheduled development when integration and acceptance tests are complete; report concrete access/data blockers without claiming progress.
