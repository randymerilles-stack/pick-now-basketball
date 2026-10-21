"""Offline, fail-closed regulation-time arithmetic, never a live verifier.

Verification flags are caller preconditions, not evidence. No current provider
or league configuration is approved to set them. No ref-based extrapolation.
"""


def remaining_regulation_seconds(period, minutes, seconds, *, regulation_periods,
                                 period_seconds, clock_semantics_verified=False,
                                 league_rules_verified=False,
                                 state_alignment_verified=False,
                                 clock_direction=None, overtime=False):
    """Return time at the observed state, or None for unqualified inputs.

Only an explicitly verified per-period countdown is supported. Overtime is
excluded because the eventual full-game settlement horizon is not yet known.
The caller must verify score/period/clock/quote alignment independently.
"""
    if any(flag is not True for flag in (clock_semantics_verified,
                                        league_rules_verified,
                                        state_alignment_verified)):
        return None
    if clock_direction != 'period_countdown' or overtime is not False:
        return None
    values = (period, minutes, seconds, regulation_periods, period_seconds)
    if any(type(value) is not int for value in values):
        return None
    if regulation_periods <= 0 or period_seconds <= 0:
        return None
    if not 1 <= period <= regulation_periods or minutes < 0 or not 0 <= seconds < 60:
        return None
    within_period = minutes * 60 + seconds
    if within_period > period_seconds:
        return None
    return (regulation_periods - period) * period_seconds + within_period
