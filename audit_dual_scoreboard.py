"""Bounded provider/ESPN NBL evidence capture; no automatic identity merge."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError

SOURCES={
    'provider':'https://moviodds.com/odds?sport=basketball&in_play=1&stats=1',
    'espn_nbl':'https://site.api.espn.com/apis/site/v2/sports/basketball/nbl/scoreboard?dates=20261023',
}


def fetch(item):
    name,url=item
    started=datetime.now(timezone.utc).isoformat()
    row={'name':name,'url':url,'started_at':started}
    stage='request'
    try:
        with urlopen(Request(url,headers={'User-Agent':'PickNowSourceAudit/1.0'}),timeout=20) as r:
            stage='http_status'
            row['http_status']=r.status
            if r.status!=200:raise ValueError('Unexpected status')
            stage='payload_size'
            raw=r.read(3_000_001)
            row['bytes_read']=len(raw)
            if len(raw)>3_000_000:raise ValueError('Oversized response')
            row['http_date']=r.headers.get('Date')
            row['http_age']=r.headers.get('Age')
            row['cache_control']=r.headers.get('Cache-Control')
        row['received_at']=datetime.now(timezone.utc).isoformat()
        row['sha256']=hashlib.sha256(raw).hexdigest()
        stage='json_decode'
        row['response']=json.loads(raw)
    except HTTPError as exc:
        # urlopen raises before entering the response context for non-2xx.
        # Preserve status without reading a rejected body or exception message.
        row['received_at']=datetime.now(timezone.utc).isoformat()
        row['http_status']=exc.code
        row['error_type']='HTTPError'
        row['error_stage']='http_status'
        exc.close()
    except Exception as exc:
        row['received_at']=datetime.now(timezone.utc).isoformat()
        row['error_type']=type(exc).__name__
        row['error_stage']=stage
    return row


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    with ThreadPoolExecutor(max_workers=2) as pool:rows=list(pool.map(fetch,SOURCES.items()))
    report={'sources':rows,'independently_aligned':False,'training_eligible':False,
            'approved_for_picks':False}
    with args.output.open('x') as f:json.dump(report,f,indent=2,allow_nan=False)
    for row in rows:
        data=row.get('response',{})
        if row['name']=='provider':
            print(json.dumps({'source':row['name'],'error':row.get('error_type'),
                'received_at':row['received_at'],'nbl_fixtures':[
                    {k:m.get(k) for k in ('id','home','away','league','score','clock','stats','kickoff_utc')}
                    for m in data.get('matches',[]) if 'NBL' in str(m.get('league'))]}))
        else:
            print(json.dumps({'source':row['name'],'error':row.get('error_type'),
                'received_at':row['received_at'],'events':[
                    {k:e.get(k) for k in ('id','date','name','status','competitions')}
                    for e in data.get('events',[])]}))
