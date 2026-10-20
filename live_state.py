"""Research readiness diagnostics; never infer periods or emit probabilities."""
import re

def assess_live_state(fixture):
    """Report structural presence separately from semantic verification."""
    score=fixture.get('score')
    clock=fixture.get('clock')
    period=fixture.get('period')
    score_present=isinstance(score,str) and re.fullmatch(r'\d+\s*-\s*\d+',score.strip()) is not None
    clock_present=(isinstance(clock,dict)
        and type(clock.get('min')) is int and clock['min']>=0
        and type(clock.get('sec')) is int and 0<=clock['sec']<60)
    period_present=(type(period) is int and period>0) or (isinstance(period,str) and bool(period.strip()))
    blockers=[]
    if not score_present:blockers.append('score_missing_or_malformed')
    if not clock_present:blockers.append('clock_missing_or_malformed')
    if not period_present:blockers.append('explicit_period_missing')
    # Presence alone cannot establish count-up/down, league length, overtime,
    # synchronized observation time, source correctness or predictive validity.
    blockers.extend(['period_and_clock_semantics_unverified',
                     'score_clock_quote_alignment_unverified',
                     'score_time_model_not_validated'])
    return {'score_present':score_present,'clock_present':clock_present,
            'explicit_period_present':bool(period_present),
            'remaining_regulation_seconds':None,'priority_ready':False,
            'blockers':blockers}
