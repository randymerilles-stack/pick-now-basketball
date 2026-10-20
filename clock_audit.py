"""Compare bounded feed observations, without extrapolating a game clock."""
from datetime import datetime, timezone
import argparse
import json
from pathlib import Path
from urllib.request import Request, urlopen
from live_state import observed_period
from prospective_capture import SOURCE, capture


def clock_seconds(fixture):
    clock=fixture.get('clock')
    if not isinstance(clock,dict):return None
    minute,second=clock.get('min'),clock.get('sec')
    if type(minute) is not int or minute<0 or type(second) is not int or not 0<=second<60:return None
    return minute*60+second


def compare_snapshots(before, after):
    previous={str(f['id']):f for f in before.get('matches',[]) if isinstance(f,dict) and f.get('id') is not None}
    transitions=[]
    for current in after.get('matches',[]):
        if not isinstance(current,dict):continue
        prior=previous.get(str(current.get('id')))
        if prior is None:continue
        # Same numeric ID is insufficient if names or competition have changed.
        if any(prior.get(k)!=current.get(k) or not current.get(k) for k in ('home','away','league')):continue
        if any(not isinstance(f.get('stats'),dict) or f['stats'].get('sport')!='basketball' for f in (prior,current)):continue
        p0,p1=observed_period(prior),observed_period(current)
        c0,c1=clock_seconds(prior),clock_seconds(current)
        same_period=p0 is not None and p0==p1
        delta=c1-c0 if same_period and c0 is not None and c1 is not None else None
        transitions.append({'fixture_id':str(current['id']),'league':current['league'],
                            'period_before':p0,'period_after':p1,
                            'clock_before_seconds':c0,'clock_after_seconds':c1,
                            'same_period_clock_delta':delta,
                            'direction_observed':'decreasing' if delta is not None and delta<0 else
                                                 'increasing' if delta is not None and delta>0 else
                                                 'unchanged' if delta==0 else 'not_comparable',
                            'clock_ref_before':prior.get('clock',{}).get('ref'),
                            'clock_ref_after':current.get('clock',{}).get('ref'),
                            'score_changed':prior.get('score')!=current.get('score'),
                            'semantics_verified':False})
    return transitions


def fetch():
    with urlopen(Request(SOURCE,headers={'User-Agent':'PickNowClockAudit/0.1'}),timeout=20) as response:
        raw=response.read(3_000_001)
        if len(raw)>3_000_000:raise ValueError('Oversized feed')
        data=json.loads(raw)
    return data,datetime.now(timezone.utc)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    before,t0=fetch();after,t1=fetch()
    report={'source':SOURCE,'received_before':t0.isoformat(),'received_after':t1.isoformat(),
            'server_time_before':before.get('server_time'),'server_time_after':after.get('server_time'),
            'transitions':compare_snapshots(before,after),
            'captures':[capture(before,t0),capture(after,t1)],
            'limitations':['Two observations cannot prove clock direction or freshness semantics.',
                          'A stopped or unchanged clock does not establish a break or remaining game time.',
                          'Records are research only, not independent games or validated training samples.'],
            'approved_for_picks':False}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    # Exclusive create prevents silently replacing earlier research evidence.
    with args.output.open('x',encoding='utf-8') as output:json.dump(report,output,indent=2,allow_nan=False)
    print(json.dumps({'output':str(args.output),'paired_real_fixtures':len(report['transitions']),
                      'directions':{direction:sum(t['direction_observed']==direction for t in report['transitions'])
                                    for direction in ('decreasing','increasing','unchanged','not_comparable')},
                      'captured_market_pairs':[len(c['observations']) for c in report['captures']],
                      'approved_for_picks':False}))


if __name__=='__main__':main()
