"""Experimental paper forecasts. Never approves a bet or independently verifies odds."""
import hashlib
import json
import math

APPROACH = 'Market probability calibration with regularized logistic offset'


def paper_forecasts(markets, report):
    experiment = report.get('calibration_experiment', {}) if isinstance(report, dict) else {}
    if not isinstance(experiment, dict):
        return []
    train, test = experiment.get('training_fixtures'), experiment.get('heldout_fixtures')
    if (experiment.get('trained') is not True or experiment.get('approach') != APPROACH
            or type(train) is not int or type(test) is not int or train < 200 or test < 100):
        return []
    offset = experiment.get('offset')
    if isinstance(offset, bool) or not isinstance(offset, (int, float)) or not math.isfinite(offset):
        return []
    version = 'market-offset-v1-' + hashlib.sha256(
        json.dumps([APPROACH, offset, train, test], allow_nan=False).encode()).hexdigest()[:12]
    by_fixture = {}
    for market in markets:
        try:
            if market.get('data_checks') != 'passed':
                continue
            age = float(market['poll_age_seconds'])
            if not math.isfinite(age) or not 0 <= age < 30:
                continue
            home, away = market['home'], market['away']
            quotes = market['quotes']
            if len(quotes) != 2 or {q['team'] for q in quotes} != {home, away}:
                continue
            h = next(q for q in quotes if q['team'] == home)
            a = next(q for q in quotes if q['team'] == away)
            line, opposite = float(h['line']), float(a['line'])
            prices = [float(h['odds']), float(a['odds'])]
            if (not all(math.isfinite(x) for x in [line, opposite, *prices])
                    or min(prices) <= 1 or abs(line + opposite) > 1e-8
                    or abs(line * 2 - round(line * 2)) > 1e-8 or line.is_integer()):
                continue  # Training only covered half-point binary outcomes, not pushes.
            market_home = (1 / prices[0]) / sum(1 / price for price in prices)
            logit = math.log(market_home / (1 - market_home)) + offset
            home_probability = 1 / (1 + math.exp(-max(-30, min(30, logit))))
            candidates = []
            for quote, probability in [(h, home_probability), (a, 1 - home_probability)]:
                odds = float(quote['odds'])
                ev = probability * odds - 1
                candidates.append(dict(
                    fixture_id=market['fixture_id'], home=home, away=away,
                    league=market.get('league'), team=quote['team'], line=float(quote['line']),
                    odds=odds, model_probability=probability, estimated_ev=ev,
                    positive_estimated_ev=ev > 0, model_version=version,
                    poll_age_seconds=age, approved_for_betting=False,
                    independently_verified=False,
                    warning='PAPER ONLY. Unvalidated probability estimate; no reliable edge established. '
                            'Provider reference odds are not independently bookmaker-verified. '
                            'Selected by highest estimated EV for simulation, even when EV is negative.'
                ))
            chosen = max(candidates, key=lambda q: q['estimated_ev'])
            previous = by_fixture.get(chosen['fixture_id'])
            if previous is None or chosen['estimated_ev'] > previous['estimated_ev']:
                by_fixture[chosen['fixture_id']] = chosen
        except (KeyError, TypeError, ValueError, OverflowError, StopIteration):
            continue
    return sorted(by_fixture.values(), key=lambda q: q['estimated_ev'], reverse=True)[:3]
