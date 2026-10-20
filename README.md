# Pick Now

Separate basketball live-feed validation website. No changes to basketball-handicap-analyzer.

Python 3.11+; no third-party packages. Start: `python app.py`. Render: Python runtime, build `python -m unittest -v`, start `python app.py`, health path `/health`, free compute where available.

The interface checks a third-party feed on demand. Reachability and schema checks do not establish odds verification. Full Game Handicap verification requires documented provider semantics, event/team mapping, full-game settlement and overtime rules, paired lines/prices, suspension and quote freshness checks. None is claimed complete. All markets and picks remain blocked.

There is no probability model. Unlocking recommendations requires historical data, a chronological out-of-sample backtest, calibration, comparison against a baseline, leakage checks, reproducible metrics and per-league applicability. Unit tests check fail-closed behavior, not predictive performance. No model probability is displayed.

Endpoints: `/`, `/health`, `/api/pick-now`. Provider failures return NO BET with diagnostic status. Health checks represent application availability, not data validity. No credentials or wager submission.
