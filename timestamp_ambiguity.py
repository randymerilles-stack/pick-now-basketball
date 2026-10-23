"""Offline diagnostics: never repair source order or certify availability."""
from play_timestamp_audit import stamp


def reversal_intervals(plays):
    intervals = []
    for previous, current in zip(plays, plays[1:]):
        try:
            before, after = stamp(previous.get('wallclock')), stamp(current.get('wallclock'))
        except (ValueError, TypeError, AttributeError):
            continue
        if after >= before:
            continue
        intervals.append({
            'previous_id': previous.get('id'), 'current_id': current.get('id'),
            'start': after.isoformat(), 'end': before.isoformat(),
            'backward_seconds': (before-after).total_seconds(),
            'same_game_state': all(previous.get(k) == current.get(k)
                                   for k in ('period', 'clock', 'homeScore', 'awayScore')),
        })
    return {'reversal_count': len(intervals), 'intervals': intervals,
            'training_eligible': False, 'approved_for_picks': False,
            'limitation': 'Diagnostic intervals only. Equal game state does not establish timestamp semantics or live availability; intervals do not identify all unsafe joins.'}
