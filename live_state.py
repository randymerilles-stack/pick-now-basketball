"""Research readiness diagnostics; never infer periods or emit probabilities."""
import re
from datetime import datetime


def observed_period(fixture):
    """Use explicit basketball stats period; never infer from clock/score."""
    direct=fixture.get('period')
    stats=fixture.get('stats')
    nested=stats.get('period') if isinstance(stats,dict) and stats.get('sport')=='basketball' else None
    valid=lambda value:type(value) is int and value>0
    if direct is not None:
        if not valid(direct) or (nested is not None and (not valid(nested) or nested!=direct)):
            return None
        return direct
    return nested if valid(nested) else None


def stats_diagnostics(fixture, server_time=None):
    stats=fixture.get('stats')
    result={'stats_present':isinstance(stats,dict),'stats_score_matches':False,
            'stats_age_seconds':None,'blockers':[]}
    if not isinstance(stats,dict):
        result['blockers'].append('basketball_stats_missing');return result
    if stats.get('sport')!='basketball':
        result['blockers'].append('stats_sport_not_real_basketball');return result
    score=fixture.get('score')
    match=re.fullmatch(r'(\d+)\s*-\s*(\d+)',score.strip()) if isinstance(score,str) else None
    points=[stats.get(side,{}).get('points') if isinstance(stats.get(side),dict) else None for side in ('home','away')]
    result['stats_score_matches']=bool(match and all(type(p) is int and p>=0 for p in points)
                                       and points==[int(v) for v in match.groups()])
    if not result['stats_score_matches']:result['blockers'].append('stats_score_mismatch_or_missing')
    try:
        reference=datetime.fromisoformat(server_time.replace('Z','+00:00'))
        updated=datetime.fromisoformat(stats['updated_at'].replace('Z','+00:00'))
        if reference.tzinfo is None or updated.tzinfo is None:raise ValueError('Timezone required')
        age=(reference-updated).total_seconds()
        result['stats_age_seconds']=age
        if not 0<=age<30:result['blockers'].append('stats_observation_outside_30s_window')
    except (AttributeError,KeyError,TypeError,ValueError):
        result['blockers'].append('stats_observation_time_unverified')
    return result


def assess_live_state(fixture, server_time=None):
    """Report structural presence separately from semantic verification."""
    score=fixture.get('score')
    clock=fixture.get('clock')
    period=observed_period(fixture)
    score_present=isinstance(score,str) and re.fullmatch(r'\d+\s*-\s*\d+',score.strip()) is not None
    clock_present=(isinstance(clock,dict)
        and type(clock.get('min')) is int and clock['min']>=0
        and type(clock.get('sec')) is int and 0<=clock['sec']<60)
    period_present=type(period) is int and period>0
    blockers=[]
    if not score_present:blockers.append('score_missing_or_malformed')
    if not clock_present:blockers.append('clock_missing_or_malformed')
    if not period_present:blockers.append('explicit_period_missing')
    stats_state=stats_diagnostics(fixture,server_time)
    blockers.extend(stats_state['blockers'])
    # Presence alone cannot establish count-up/down, league length, overtime,
    # synchronized observation time, source correctness or predictive validity.
    blockers.extend(['period_and_clock_semantics_unverified',
                     'score_clock_quote_alignment_unverified',
                     'score_time_model_not_validated'])
    return {'score_present':score_present,'clock_present':clock_present,
            'explicit_period_present':bool(period_present),
            'period_observed':period,'stats_diagnostics':stats_state,
            'remaining_regulation_seconds':None,'priority_ready':False,
            'blockers':blockers}
