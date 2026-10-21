# Source semantics re-audit — 21 October 2026, 13:33 Perth

Source inspected: https://moviodds.com/doc (current public documentation, sections 4, 6, 7, 10).

Findings:
- The page describes basketball stats.period, per-period scores, and half-based competitions. It still does not define clock.min/sec/ref direction or synchronization guarantees. Explicit period presence therefore remains insufficient for remaining-time conversion.
- Stats delivery is best effort; a dropped update may only be replaced when another change arrives. Receipt time alone cannot establish a synchronized scoreboard snapshot.
- A market-specific group_status.polled_at now matters: fixture polled_at can advance when a different market was read. Existing validation.py checks fixture polled_at but has no group_status check. Consequently existing data_checked labels do not establish fresh Full Game Handicap group confirmation.
- Results.finished_at is documented as last seen live, approximately the actual finish. Provider results remain research labels, not independent settlement verification.
- History/closing expose fixture_ids/prematch_id to resolve provider aliases; historical score/clock alignment remains unestablished.

Required next implementation:
Add strict Full Game Handicap group freshness rejection using the exact selected group ID and its own polled_at; reject missing/malformed/future/stale group confirmation and test a fresh fixture with an old handicap group. Preserve stable-price ts semantics. Apply to research capture and paper feed validation, test then verify deployed release before claiming protection.
Keep score/time training and Priority Pick disabled while clock/rule/alignment requirements remain unmet.

No source-clock semantics were inferred or verified in this audit. No new forecast or model accuracy result.
