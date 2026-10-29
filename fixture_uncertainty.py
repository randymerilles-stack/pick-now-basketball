"""Descriptive fixture-block bootstrap for already scored frozen forecasts.

Resample canonical events, never ticks or opposing sides. This does not train,
approve, select timing windows, establish power or verify source evidence.
"""
import math
import random
from statistics import mean


def _number(value):
    if type(value) not in (int, float) or not math.isfinite(value):
        raise ValueError('Finite numeric score required')
    return value


def _percentile(ordered, fraction):
    position = (len(ordered)-1)*fraction
    lower = math.floor(position)
    upper = math.ceil(position)
    return ordered[lower] + (ordered[upper]-ordered[lower])*(position-lower)


def fixture_bootstrap(report, *, resamples=2000, seed=0):
    """95% percentile interval of equal-event candidate-minus-baseline Brier.

    Input must be a forecast_scoring report with one aggregate per event.
    Caller must predeclare this procedure and retain the locked test manifest.
    Two events permits arithmetic, not adequate statistical evidence.
    """
    if type(resamples) is not int or not 1000 <= resamples <= 20000 or type(seed) is not int:
        raise ValueError('Use integer resamples in [1000,20000] and integer seed')
    if (not isinstance(report, dict) or report.get('approved_for_picks') is not False or
            report.get('status') not in ('descriptive_only', 'insufficient_data')):
        raise ValueError('Unapproved descriptive scoring report required')
    rows = report.get('events')
    if not isinstance(rows, list) or type(report.get('independent_events')) is not int or report['independent_events'] != len(rows):
        raise ValueError('Event count mismatch')
    differences, seen = [], set()
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError('Invalid event aggregate')
        event = row.get('canonical_event_id')
        if not isinstance(event, str) or not event.strip() or event in seen:
            raise ValueError('Distinct canonical event IDs required')
        seen.add(event)
        c, b = (_number(row.get(k)) for k in ('candidate_brier', 'baseline_brier'))
        d = _number(row.get('paired_difference'))
        if not 0 <= c <= 1 or not 0 <= b <= 1 or not math.isclose(d, c-b, rel_tol=0, abs_tol=1e-12):
            raise ValueError('Invalid paired Brier scores')
        differences.append((event, d))
    # Canonical ordering makes seeded results invariant to input row order.
    values = [d for _, d in sorted(differences)]
    n = len(values)
    if n*resamples > 10_000_000:
        raise ValueError('Bootstrap work budget exceeded; use fewer resamples')
    result = dict(method='equal_fixture_percentile_bootstrap', confidence_level=.95,
                  independent_events=n, resamples=resamples, seed=seed,
                  paired_mean=mean(values) if n else None, interval=None,
                  approved_for_picks=False, statistical_power_established=False,
                  limitations=['Descriptive only: negative difference favors candidate.',
                               'Assumes independent canonical games; between-game dependence remains unchecked.',
                               'Small or constant samples can yield misleadingly narrow intervals.',
                               'No source verification, calibration, test-power or later replication established.'])
    if n < 2:
        return dict(result, status='insufficient_independent_events')
    rng = random.Random(seed)
    draws = sorted(mean(values[rng.randrange(n)] for _ in range(n)) for _ in range(resamples))
    interval = [_percentile(draws, .025), _percentile(draws, .975)]
    result.update(interval=interval, status='descriptive_interval_only',
                  degenerate_sample=min(values)==max(values))
    return result
