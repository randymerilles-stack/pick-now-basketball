"""Capture contemporaneous research observations; never emit betting picks.

One bounded run by default. Raw observations live in git-ignored .audit-cache.
Example: python prospective_capture.py --league 'Japan B League One'
Keeping a web dashboard open does not run this collector or label outcomes.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from urllib.request import Request, urlopen
from validation import inspect_feed
from live_state import assess_live_state, observed_period

SOURCE='https://moviodds.com/odds?sport=basketball&in_play=1&stats=1'
ROOT=Path(__file__).resolve().parent


def capture(data, received_at=None):
    received_at=received_at or datetime.now(timezone.utc)
    checked=inspect_feed(data,checked_at=received_at)
    fixtures={str(f.get('id')):f for f in data.get('matches',[]) if isinstance(f,dict)}
    observations=[]
    for market in checked.get('data_checked_markets',[]):
        fixture=fixtures[market['fixture_id']]
        observations.append({
            'fixture_id':market['fixture_id'],'market_id':market['market_id'],
            'league':market['league'],'home':market['home'],'away':market['away'],
            'score_observed':fixture.get('score'),'clock_observed':fixture.get('clock'),
            # Never infer a quarter from a clock or final-score magnitude.
            'period_observed':observed_period(fixture),
            'stats_observed':fixture.get('stats'),
            'live_state_readiness':assess_live_state(fixture,data.get('server_time')),
            'polled_at':fixture.get('polled_at'),'quotes':market['quotes'],
            'independently_verified':False,'outcome':None,
        })
    raw=json.dumps(data,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
    return {'schema_version':2,'source':SOURCE,
            'received_at':received_at.isoformat(),'server_time':data.get('server_time'),
            'source_sha256':hashlib.sha256(raw).hexdigest(),
            'validation_status':checked.get('validation_status'),
            'rejected':checked.get('rejected',{}),'observations':observations,
            'approved_for_picks':False}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--league',required=True,help='Exact provider league name')
    parser.add_argument('--output',type=Path,default=ROOT/'.audit-cache'/'prospective.jsonl')
    args=parser.parse_args()
    request=Request(SOURCE,headers={'User-Agent':'PickNowResearchCapture/0.1'})
    with urlopen(request,timeout=20) as response:
        if response.status!=200:raise ValueError('Unexpected feed HTTP status')
        raw=response.read(3_000_001)
        if len(raw)>3_000_000:raise ValueError('Oversized feed')
        data=json.loads(raw)
    record=capture(data)
    record['target_league']=args.league
    record['observations']=[r for r in record['observations'] if r['league']==args.league]
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('a',encoding='utf-8') as output:
        output.write(json.dumps(record,sort_keys=True,allow_nan=False)+'\n')
    print(json.dumps({'received_at':record['received_at'],'target_league':args.league,
                      'captured_market_pairs':len(record['observations']),
                      'unique_fixtures':len({r['fixture_id'] for r in record['observations']}),
                      'independently_verified':False,'approved_for_picks':False}))

if __name__=='__main__':main()
