"""Report exact-name live overlap candidates; never certify identity or odds."""
def coverage(capture):
    sources = capture.get('sources', [])
    provider = next((s for s in sources if s.get('name') == 'provider'), {})
    fixtures = provider.get('fixtures', [])
    live = []
    candidates = []
    errors = [s.get('name') for s in sources if s.get('error_type')]
    for source in sources:
        if source.get('name') == 'provider':
            continue
        for event in source.get('events', []):
            if event.get('status', {}).get('type', {}).get('state') != 'in':
                continue
            live.append(event.get('id'))
            comps = event.get('competitions') or []
            if len(comps) != 1:
                continue
            teams = comps[0].get('competitors') or []
            home = [c.get('team', {}).get('displayName') for c in teams if c.get('homeAway') == 'home']
            away = [c.get('team', {}).get('displayName') for c in teams if c.get('homeAway') == 'away']
            if len(teams) != 2 or len(home) != 1 or len(away) != 1 or not home[0] or not away[0]:
                continue
            matches = [f for f in fixtures if f.get('in_play') is True and f.get('home') == home[0] and f.get('away') == away[0]]
            if len(matches) == 1:
                candidates.append({'source': source['name'], 'event_id': event['id'], 'fixture_id': matches[0]['id']})
    return {'provider_fixture_count': len(fixtures), 'live_scoreboard_event_ids': live,
            'exact_name_candidates': candidates, 'source_errors': errors,
            'training_eligible': False, 'approved_for_picks': False,
            'limitation': 'Exact names are candidates only; aliases, kickoff, league, clock and odds verification remain unresolved. No candidates is not proof of global coverage absence.'}
