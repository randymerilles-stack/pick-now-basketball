"""Reproduce the read-only archive audit and odds-calibration research sample.

Run: python audit_history.py --end 2026-10-19 --days 7 --limit 360
Raw endpoint responses stay in .audit-cache (excluded from Git).
This program cannot enable live picks.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta, timezone
import json
import math
from pathlib import Path
import threading
import time
from urllib.error import HTTPError
from urllib.request import urlopen
from calibration import audit, stamp

ROOT = Path(__file__).resolve().parent
LOCK = threading.Lock()
LAST = 0.

def get_json(url):
    global LAST
    with LOCK:
        time.sleep(max(0, .7 - (time.monotonic() - LAST)))
        LAST = time.monotonic()
    try:
        with urlopen(url, timeout=20) as response:
            raw=response.read(12_000_001)
            if len(raw)>12_000_000:raise ValueError('Response too large')
            return json.loads(raw)
    except HTTPError as exc:
        if exc.code in (429,503):
            try:delay=min(60,max(3,int(exc.headers.get('Retry-After','5'))))
            except ValueError:delay=5
            with LOCK:LAST=max(LAST,time.monotonic()+delay)
        raise

def eligible(f):
    return (f.get('status')=='finished' and
            all(isinstance(f.get(k),str) and f[k] for k in
                ('fixture_id','home','away','league','final_score','finished_at')) and
            not any(x in f['league'].lower() for x in
                    ('ebasket','esport','cyber','simulated','virtual')))

def extract(f,h):
    if h.get('truncated'):return None
    groups={}
    for q in h.get('points',[]):
        if (q.get('line')!='Line' or q.get('group_name')!='Game' or
                str(q.get('group_id'))!='112' or q.get('suspended',False)):
            continue
        try:
            line=float(q.get('handicap',q.get('label')));price=float(q['odds_dec'])
        except (TypeError,ValueError,KeyError):continue
        if not math.isfinite(line) or not math.isfinite(price) or price<=1:continue
        # Restrict the binary research outcome to half-point lines: no push.
        if abs(line*2-round(line*2))>1e-6 or line.is_integer():continue
        groups.setdefault((q['ts'],str(q.get('market_id')),abs(line)),[]).append(
            (q.get('side'),line,price,str(q.get('sel_id'))))
    for (when,_,_),pair in sorted(groups.items()):
        if (len(pair)!=2 or {q[0] for q in pair}!={f['home'],f['away']} or
                len({q[3] for q in pair})!=2 or abs(sum(q[1] for q in pair))>1e-8):
            continue
        if stamp(when)>=stamp(f['finished_at']):continue
        home=next(q for q in pair if q[0]==f['home'])
        away=next(q for q in pair if q[0]==f['away'])
        hs,as_=map(int,f['final_score'].split('-'))
        return dict(fixture_id=f['fixture_id'],fixture_family=h.get('fixture_ids') or [f['fixture_id']],
                    league=f['league'],decision_at=when,finished_at=f['finished_at'],
                    outcome_available_at=max(f['finished_at'],f.get('updated_at',f['finished_at']),key=stamp),
                    home_line=home[1],home_price=home[2],away_price=away[2],
                    market_home_probability=(1/home[2])/((1/home[2])+(1/away[2])),
                    home_covered=int(hs-as_+home[1]>0),final_score=f['final_score'])
    return None

def run(end,days,limit,workers):
    cache=ROOT/'.audit-cache';cache.mkdir(exist_ok=True)
    fixtures={};sources=[];raw_count=0
    for i in range(days):
        day=(end-timedelta(days=i)).isoformat();p=cache/f'results-{day}.json'
        d=json.loads(p.read_text()) if p.exists() else get_json(
            'https://moviodds.com/results?sport=basketball&date='+day)
        p.write_text(json.dumps(d));sources.append(d.get('source'))
        raw_count+=len(d.get('results',[]))
        for f in d.get('results',[]):
            if eligible(f):fixtures[f['fixture_id']]=f
    ordered=sorted(fixtures.values(),key=lambda f:f['finished_at'])
    chosen=ordered if len(ordered)<=limit else [ordered[int(i*(len(ordered)-1)/(limit-1))] for i in range(limit)]
    def one(f):
        p=cache/(f['fixture_id']+'.json')
        try:
            d=json.loads(p.read_text()) if p.exists() else {'fixture':f,'history':get_json(
                'https://moviodds.com/history?fi='+f['fixture_id']+'&group=112&limit=5000')}
            p.write_text(json.dumps(d));return extract(f,d['history'])
        except Exception:return None
    rows=[];seen=set()
    with ThreadPoolExecutor(max_workers=workers) as pool:
        for row in pool.map(one,chosen):
            if row and not seen.intersection(row['fixture_family']):
                rows.append(row);seen.update(row['fixture_family'])
    rows.sort(key=lambda r:stamp(r['decision_at']))
    (ROOT/'calibration_sample.json').write_text(json.dumps(rows,indent=2)+'\n')
    experiment=audit(rows)
    (ROOT/'calibration_report.json').write_text(json.dumps(experiment,indent=2)+'\n')
    coverage=dict(checked_at=datetime.now(timezone.utc).isoformat(),end_date=end.isoformat(),
                  days_requested=days,result_rows=raw_count,eligible_real_fixtures=len(fixtures),
                  histories_requested=len(chosen),matched_independent_fixtures=len(rows),
                  unmatched_or_failed=len(chosen)-len(rows),result_archive_sources=sources)
    (ROOT/'audit_coverage.json').write_text(json.dumps(coverage,indent=2)+'\n')
    print(json.dumps({'coverage':coverage,'experiment':experiment},indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--end',type=date.fromisoformat,required=True)
    p.add_argument('--days',type=int,default=7)
    p.add_argument('--limit',type=int,default=360)
    p.add_argument('--workers',type=int,default=3)
    args=p.parse_args()
    if not(1<=args.days<=30 and 2<=args.limit<=1000 and 1<=args.workers<=6):
        p.error('Use days 1..30, limit 2..1000, workers 1..6')
    run(args.end,args.days,args.limit,args.workers)
