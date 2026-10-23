"""Cross-source observations are corroboration, never model qualification."""
from datetime import datetime
import math
import re


def stamp(value):
    dt=datetime.fromisoformat(value.replace('Z','+00:00'))
    if dt.tzinfo is None:raise ValueError('Timezone required')
    return dt


def compare_nbl(fixture, event):
    result={'identity_matches':False,'score_matches':False,'period_matches':False,
            'provider_stats_score_matches':False,
            'clock_delta_seconds':None,'clock_matches':False,
            'training_eligible':False,'approved_for_picks':False}
    try:
        if fixture.get('sport')!='basketball' or fixture.get('league')!='Australia NBL':return result
        competitions=event['competitions']
        if len(competitions)!=1:return result
        competition=competitions[0]
        if str(competition['id'])!=str(event['id']):return result
        competitors=competition['competitors']
        if len(competitors)!=2:return result
        teams={c['homeAway']:c for c in competitors}
        if set(teams)!={'home','away'}:return result
        if any(fixture[s]!=teams[s]['team']['displayName'] for s in ('home','away')):return result
        if stamp(fixture['kickoff_utc'])!=stamp(event['date']):return result
        result['identity_matches']=True
        stats=fixture['stats']
        score=re.fullmatch(r'(\d+)\s*-\s*(\d+)',fixture['score'])
        points=[stats[s]['points'] for s in ('home','away')]
        result['provider_stats_score_matches']=bool(score and all(type(v) is int and v>=0 for v in points)
            and points==[int(v) for v in score.groups()])
        status=event['status']
        if status['type']['state']!='in' or status['type']['completed'] is not False:return result
        if stats.get('sport')!='basketball':return result
        period=stats['period']
        ep=status['period']
        result['period_matches']=type(period) is int and type(ep) is int and period>0 and period==ep
        points=[teams[s]['score'] for s in ('home','away')]
        if all(isinstance(v,str) and re.fullmatch(r'\d+',v) for v in points):
            score=re.fullmatch(r'(\d+)\s*-\s*(\d+)',fixture['score'])
            result['score_matches']=bool(score and [int(v) for v in score.groups()]==[int(v) for v in points])
        clock=fixture['clock']
        minute,second=clock['min'],clock['sec']
        ec=status['clock']
        if (type(minute) is int and minute>=0 and type(second) is int and 0<=second<60
            and type(ec) in (int,float) and math.isfinite(ec) and ec>=0
            and result['period_matches']):
            result['clock_delta_seconds']=minute*60+second-ec
            result['clock_matches']=result['clock_delta_seconds']==0
    except (KeyError,TypeError,ValueError,AttributeError):
        pass
    return result
