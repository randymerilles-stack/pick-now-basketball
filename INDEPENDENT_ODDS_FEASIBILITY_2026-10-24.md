# Independent odds source feasibility — 24 October 2026
Research only. No live integration, trained model or qualified Priority Pick.

Official pages retrieved today:
- https://the-odds-api.com/
- https://the-odds-api.com/liveapi/guides/v4/
- https://the-odds-api.com/sports-odds-data/bookmaker-apis.html
- https://the-odds-api.com/sports-odds-data/update-intervals.html

Findings: Starter offers 500 monthly credits, most bookmakers and markets, but excludes historical odds. API key obtained by email is required. Featured in-play handicaps update every 40 seconds; this cadence cannot guarantee the existing 30-second freshness gate. Do not relax that gate or equate request receipt with quote freshness.

Critical bookmaker limitation: the official bookmaker list restricts bet365_au to paid subscriptions and AFL/NRL h2h/spreads/totals. Thus this documented route does not establish independent Bet365 basketball quote verification. Other bookmakers could support separate market research, but their differing lines/prices cannot authenticate the existing Bet365 quote. Same-event matching is necessary but insufficient; scope, overtime/settlement rules and timestamp meaning still require verification.

Budget check: at one market and one region, a two-hour session with 40-second sampling uses 180 credits; 500 supports two complete sessions before other calls. At 60 seconds it uses 120, supporting four. These assume one sport-wide request per interval, not one per fixture. Quota headers must govern any actual acquisition. Free tier is suitable only for bounded feasibility sampling, not continuous coverage or guaranteed adequate training history.

Validation performed: Python arithmetic assertions for both budgets and 40>30 passed. No predictive test performed and no API request with credentials made. Current authoritative validation.py blob 92ce4dbb5b9c78e28539dd39ad6917ead62ac638 still uses MAX_POLL_AGE=30. Available connector registry has no dedicated odds-source connector. This is not proof that no owner credential exists; Render secret values were not retrieved or printed.

Decision: do not ask owner to sign up for this candidate as if it resolves Bet365 basketball verification. Do not buy a plan or deploy an adapter. Next: assess BALLDONTLIE official bookmaker/market entitlements and live-update/settlement documentation. If no usable independent same-book source can be established, record the exact source-access decision and pause development instead of accumulating unqualified ticks. Preserve working Postgres auth and all paper/approval gates.
