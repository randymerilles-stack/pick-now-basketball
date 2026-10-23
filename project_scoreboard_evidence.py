"""Project public-source evidence without treating matching state as verified."""
from datetime import datetime
import json
from pathlib import Path
import sys
from scoreboard_alignment import compare_nbl
import validation

report=json.loads(Path(sys.argv[1]).read_text())
sources={r['name']:r for r in report['sources']}
p=sources['provider']; e=sources['espn_nbl']
fixtures=[f for f in p.get('response',{}).get('matches',[]) if str(f.get('id'))=='202674359']
events=[x for x in e.get('response',{}).get('events',[]) if x.get('id')=='401875274']
out={'sources':[{k:r.get(k) for k in ('name','url','started_at','received_at','sha256',
                                   'http_date','http_age','cache_control','error_type')}
                for r in report['sources']], 'training_eligible':False,'approved_for_picks':False}
if len(fixtures)==len(events)==1:
    f=fixtures[0];event=events[0]
    out['comparison']=compare_nbl(f,event)
    out['provider_fixture']={k:f.get(k) for k in ('id','sport','league','home','away','kickoff_utc',
                                'score','clock','stats','polled_at','group_status')}
    out['provider_fixture']['quotes']=[q for q in f.get('quotes',[]) if str(q.get('group_id'))=='112']
    out['espn_event']={k:event.get(k) for k in ('id','date','name','status')}
    out['espn_event']['competitions']=[{'id':c['id'],'format':c.get('format'),
        'competitors':[{k:t.get(k) for k in ('id','homeAway','score','linescores')} | {
            'team':{k:t['team'].get(k) for k in ('id','displayName')}}
            for t in c.get('competitors',[])]} for c in event.get('competitions',[])]
    checked=validation.inspect_feed(p['response'],checked_at=datetime.fromisoformat(p['received_at']))
    out['data_checked_handicap_pairs']=[m for m in checked.get('data_checked_markets',[])
                                       if m['fixture_id']=='202674359']
    out['pair_count']=len(out['data_checked_handicap_pairs'])
    out['receipt_gap_seconds']=abs((datetime.fromisoformat(e['received_at'])-
                                   datetime.fromisoformat(p['received_at'])).total_seconds())
else:out['comparison']={'status':'requested_fixture_or_event_unavailable'}
out['limitations']=['Separate websites may share upstream data; this is corroboration only.',
    'HTTP receipt proximity is not an event-time synchronization guarantee.',
    'A price from this provider is not independently verified bookmaker odds.',
    'No model was trained or forecast evaluated.']
with Path(sys.argv[2]).open('x') as output:json.dump(out,output,indent=2,allow_nan=False)
print(json.dumps({k:out.get(k) for k in ('comparison','pair_count','receipt_gap_seconds')}))
