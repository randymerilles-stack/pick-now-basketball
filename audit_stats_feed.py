"""Bounded structural audit of opt-in stats; no model or betting approval."""
import json
from datetime import datetime, timezone
from urllib.request import Request, urlopen
from live_state import assess_live_state
from prospective_capture import SOURCE, capture


def audit(data, received_at):
    fixtures=data.get('matches',[])
    real=[f for f in fixtures if isinstance(f.get('stats'),dict) and f['stats'].get('sport')=='basketball']
    states=[assess_live_state(f,data.get('server_time')) for f in real]
    record=capture(data,received_at)
    return {'source':SOURCE,'received_at':received_at.isoformat(),'server_time':data.get('server_time'),
            'fixtures_seen':len(fixtures),'real_basketball_stats_fixtures':len(real),
            'explicit_period_fixtures':sum(s['explicit_period_present'] for s in states),
            'stats_score_matches':sum(s['stats_diagnostics']['stats_score_matches'] for s in states),
            'stats_within_30s':sum(s['stats_diagnostics']['stats_age_seconds'] is not None
                                  and 0<=s['stats_diagnostics']['stats_age_seconds']<30 for s in states),
            'captured_market_pairs':len(record['observations']),
            'priority_ready':False,'approved_for_picks':False,
            'limitations':['Structural coverage only; no independent source verification.',
                          'Stats updated_at may mean last change, not last observation; strict age gate is conservative.',
                          'Clock direction, league duration, overtime and joint observation semantics need validation.',
                          'No validated score/time or timing-window probability model.']}


if __name__=='__main__':
    with urlopen(Request(SOURCE,headers={'User-Agent':'PickNowStatsAudit/0.1'}),timeout=20) as response:
        raw=response.read(3_000_001)
        if len(raw)>3_000_000:raise ValueError('Oversized feed')
        data=json.loads(raw)
    print(json.dumps(audit(data,datetime.now(timezone.utc)),indent=2,allow_nan=False))
