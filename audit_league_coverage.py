"""Bounded real-league archive census, without re-fitting a reviewed holdout.

Example: python audit_league_coverage.py --end 2026-10-19 --days 30
Outputs a research feasibility report, never picks or model approval.
"""
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta, timezone
import json
from pathlib import Path
from audit_history import get_json,eligible

ROOT=Path(__file__).resolve().parent

def census(end,days):
    cache=ROOT/'.audit-cache';cache.mkdir(exist_ok=True)
    dates=[(end-timedelta(days=i)).isoformat() for i in range(days)]
    def one(day):
        path=cache/f'results-{day}.json'
        # Reuse an earlier raw read-only audit when present.
        previous=ROOT.parent/'audit-expanded'/path.name
        try:
            if path.exists():data=json.loads(path.read_text())
            elif previous.exists():data=json.loads(previous.read_text())
            else:
                data=get_json('https://moviodds.com/results?sport=basketball&date='+day)
                path.write_text(json.dumps(data))
            if data.get('source')!='postgres':
                return day,{'error':'archive_not_confirmed','source':data.get('source')},[]
            rows=[r for r in data.get('results',[]) if eligible(r) and
                  '3x3' not in r['league'].lower() and
                  not any(s in (' '+r['home']+' '+r['away']).lower() for s in
                          ('ebasket','esport','cyber','simulated','virtual','nba 2k'))]
            return day,{'source':'postgres','result_count':len(data.get('results',[])),
                        'eligible_5v5_candidates':len(rows)},rows
        except Exception as error:return day,{'error':type(error).__name__},[]
    days_report={};fixtures={}
    with ThreadPoolExecutor(max_workers=2) as pool:
        for day,summary,rows in pool.map(one,dates):
            days_report[day]=summary
            for row in rows:fixtures[row['fixture_id']]=row
    leagues=Counter(r['league'] for r in fixtures.values())
    return {'checked_at':datetime.now(timezone.utc).isoformat(),
            'start_date':dates[-1],'end_date':dates[0],'days_requested':days,
            'archive_days':days_report,'eligible_unique_fixtures':len(fixtures),
            'league_counts':dict(leagues.most_common()),
            'leagues_with_at_least_300_result_candidates':[k for k,v in leagues.items() if v>=300],
            'model_approved':False,
            'notes':['Result counts are an upper bound: paired history, timing, alias and settlement checks can reduce usable fixtures.',
                     '300 results is only an existing research sample gate, not proof of statistical power or profitable edge.',
                     'Existing 108-game reviewed holdout cannot be reused as an untouched confirmation test.',
                     'Source postgres confirms archive access, not archive completeness or independent official settlement.']}

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--end',required=True,type=date.fromisoformat)
    parser.add_argument('--days',type=int,default=30)
    parser.add_argument('--output',type=Path,default=ROOT/'single_league_feasibility.json')
    args=parser.parse_args()
    if not 1<=args.days<=30:parser.error('--days must be 1..30')
    report=census(args.end,args.days)
    args.output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'checked_at':report['checked_at'],'days_requested':report['days_requested'],
                      'eligible_unique_fixtures':report['eligible_unique_fixtures'],
                      'top_leagues':list(report['league_counts'].items())[:10],
                      'leagues_at_300':report['leagues_with_at_least_300_result_candidates'],
                      'failed_days':{k:v for k,v in report['archive_days'].items() if 'error' in v}},indent=2))
