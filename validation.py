"""Provider-mapped basketball Game/Line checks. Not settlement verification."""
from collections import Counter, defaultdict
from datetime import datetime, timezone
import math

DOCS = 'https://moviodds.com/bet365-nba-odds-api/'
MAX_POLL_AGE = 30

def timestamp(value):
    if not isinstance(value, str):
        raise ValueError('Missing timestamp')
    value = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if value.tzinfo is None:
        raise ValueError('Timezone required')
    return value

def number(value):
    if isinstance(value, bool):
        raise ValueError('Boolean is not a number')
    value = float(value)
    if not math.isfinite(value):
        raise ValueError('Non-finite number')
    return value

def inspect_feed(data, checked_at=None):
    if not isinstance(data, dict) or not isinstance(data.get('matches'), list):
        raise ValueError('Unsupported feed schema')
    checked_at = checked_at or datetime.now(timezone.utc)
    matches = data['matches']
    rejected = Counter()
    candidates = []
    fixtures = []
    quotes_seen = sum(len(m.get('quotes', [])) for m in matches
                      if isinstance(m, dict) and isinstance(m.get('quotes'), list))
    try:
        server = timestamp(data.get('server_time'))
        if abs((checked_at - server).total_seconds()) > 60:
            raise ValueError('Feed clock too far from request clock')
    except (ValueError, TypeError):
        return dict(games_seen=len(matches), quotes_seen=quotes_seen,
                    data_checked_markets=[], data_checked_market_count=0,
                    fixtures=[], markets=[], verified_market_count=0,
                    validation_status='invalid_feed_timestamp',
                    rejected={'invalid_feed_timestamp': len(matches)})
    ids = Counter(str(m.get('id')) for m in matches if isinstance(m, dict))
    for m in matches:
        if not isinstance(m, dict):
            rejected['invalid_fixture'] += 1
            continue
        fid = str(m.get('id', ''))
        home, away = m.get('home'), m.get('away')
        if (not fid or ids[fid] != 1 or m.get('sport') != 'basketball'
                or m.get('in_play') is not True or not isinstance(home, str)
                or not isinstance(away, str) or not home or not away or home == away):
            rejected['invalid_fixture_identity'] += 1
            continue
        if any(x in str(m.get('league', '')).lower() for x in
               ('ebasket', 'esport', 'cyber', 'simulated', 'virtual')):
            rejected['virtual_basketball_excluded'] += 1
            continue
        try:
            age = (max(server, checked_at) - timestamp(m.get('polled_at'))).total_seconds()
            fresh = -5 <= age <= MAX_POLL_AGE
        except (TypeError, ValueError):
            age, fresh = None, False
        fixtures.append(dict(id=fid, home=home, away=away,
                             league=m.get('league'), score=m.get('score'),
                             poll_age_seconds=round(age, 1) if age is not None else None,
                             freshness='fresh' if fresh else 'stale_or_missing'))
        if not fresh:
            rejected['stale_or_missing_poll'] += 1
            continue
        groups = defaultdict(list)
        quotes = m.get('quotes')
        if not isinstance(quotes, list):
            rejected['invalid_quotes'] += 1
            continue
        for q in quotes:
            if not isinstance(q, dict):
                rejected['invalid_quote'] += 1
                continue
            if (str(q.get('group_id')) != '112' or q.get('group_name') != 'Game'
                    or q.get('line') != 'Line' or q.get('period') not in (None, '')
                    or q.get('phase') != 'inplay'):
                rejected['not_live_full_game_line'] += 1
                continue
            if str(q.get('fixture_id')) != fid or not q.get('market_id') or not q.get('sel_id'):
                rejected['invalid_quote_identity'] += 1
                continue
            if q.get('suspended', False) is not False:
                rejected['suspended_or_invalid_flag'] += 1
                continue
            try:
                price = number(q.get('odds_dec'))
                line = number(q.get('handicap', q.get('label')))
                qt = timestamp(q.get('ts'))
                if price <= 1 or qt > server or q.get('side') not in (home, away):
                    raise ValueError('Invalid quote')
            except (TypeError, ValueError, OverflowError):
                rejected['invalid_price_line_team_or_time'] += 1
                continue
            groups[(str(q['market_id']), abs(line))].append(
                dict(team=q['side'], line=line, odds=price, selection_id=str(q['sel_id'])))
        for (mid, _), pair in groups.items():
            if (len(pair) != 2 or {q['team'] for q in pair} != {home, away}
                    or len({q['selection_id'] for q in pair}) != 2
                    or abs(sum(q['line'] for q in pair)) > 1e-8):
                rejected['unpaired_or_mismatched_line'] += 1
                continue
            pair.sort(key=lambda q: q['team'] != home)
            candidates.append(dict(fixture_id=fid, market_id=mid, home=home, away=away,
                                   league=m.get('league'), score=m.get('score'),
                                   poll_age_seconds=round(age, 1), quotes=pair,
                                   data_checks='passed', settlement='not_independently_verified'))
    return dict(games_seen=len(matches), quotes_seen=quotes_seen,
                data_checked_markets=candidates, data_checked_market_count=len(candidates),
                fixtures=fixtures, markets=[], verified_market_count=0,
                server_time=server.isoformat(), rejected=dict(rejected),
                validation_status='provider_mapping_checked_settlement_pending')
