"""Offline paired home/away handicap forecast scoring; no model approval.

Each forecast contains home win/loss/push probabilities for candidate and
market-only calibration. Away probabilities must be their exact complements.
Three-class Brier is half the summed squared error (binary-compatible scale).
Average decisions within each canonical event, then weight events equally.
External verification flags and timestamps are caller evidence requirements;
this utility cannot prove immutable persistence or adequate test power.
"""
from collections import Counter, defaultdict
import math
from statistics import mean
from evaluation_split import timestamp


def numeric(value):
    if isinstance(value, bool) or not isinstance(value, (float, int)) or not math.isfinite(value):
        raise ValueError('invalid_number')
    return value


def probabilities(value):
    if not isinstance(value, (list, tuple)) or len(value) != 3:
        raise ValueError('invalid_probabilities')
    values = [numeric(x) for x in value]
    if any(x < 0 or x > 1 for x in values) or not math.isclose(sum(values), 1, abs_tol=1e-9):
        raise ValueError('invalid_probabilities')
    return values


def score_frozen_forecasts(forecasts, outcomes, *, test_event_ids, model_versions):
    """Score only explicitly locked test events, rejecting whole invalid games.

Outcomes are separate from forecasts. Model freeze and forecast persistence
must precede the finished result, not merely its later retrieval timestamp.
Repeated decision IDs reject the event, preventing accidental extra weighting.
"""
    if (not isinstance(test_event_ids, (list, tuple)) or
            any(not isinstance(e, str) or not e.strip() for e in test_event_ids) or
            len(set(test_event_ids)) != len(test_event_ids)):
        raise ValueError('Unique canonical test IDs required')
    if (not isinstance(model_versions, (tuple, list)) or len(model_versions) != 2 or
            any(not isinstance(v, str) or not v.strip() for v in model_versions)):
        raise ValueError('Candidate and baseline versions required')
    allowed = set(test_event_ids)
    groups = defaultdict(list)
    labels = defaultdict(list)
    rejected = Counter()
    for result in outcomes:
        if isinstance(result, dict) and isinstance(result.get('canonical_event_id'), str):
            labels[result.get('canonical_event_id')].append(result)
    for row in forecasts:
        if (not isinstance(row, dict) or not isinstance(row.get('canonical_event_id'), str)
                or row.get('canonical_event_id') not in allowed):
            rejected['outside_locked_test'] += 1
            continue
        groups[row['canonical_event_id']].append(row)
    scored = []
    for event, rows in sorted(groups.items()):
        try:
            if len(labels[event]) != 1:
                raise ValueError('missing_or_duplicate_outcome')
            outcome = labels[event][0]
            if outcome.get('settlement_verified') is not True:
                raise ValueError('unverified_settlement')
            margin = numeric(outcome.get('final_home_margin'))
            if type(margin) is not int:
                raise ValueError('invalid_final_score_margin')
            finished = timestamp(outcome.get('finished_at'))
            available = timestamp(outcome.get('available_at'))
            if finished > available:
                raise ValueError('invalid_chronology')
            seen = set()
            candidate, baseline, pushes = [], [], 0
            for row in rows:
                if any(row.get(k) is not True for k in
                       ('identity_verified', 'state_verified', 'odds_verified', 'forecast_persisted')):
                    raise ValueError('unverified_forecast')
                decision_id = row.get('decision_id')
                if not isinstance(decision_id, str) or not decision_id or decision_id in seen:
                    raise ValueError('duplicate_or_missing_decision')
                seen.add(decision_id)
                if any(not isinstance(row.get(k), str) or not row[k].strip()
                       for k in ('candidate_version', 'baseline_version')):
                    raise ValueError('missing_model_version')
                if (row['candidate_version'], row['baseline_version']) != tuple(model_versions):
                    raise ValueError('model_version_mismatch')
                decision = timestamp(row.get('decision_at'))
                persisted = timestamp(row.get('persisted_at'))
                frozen = timestamp(row.get('model_frozen_at'))
                if not frozen <= decision <= persisted < finished:
                    raise ValueError('invalid_chronology')
                line = numeric(row.get('home_line'))
                away_line = numeric(row.get('away_line'))
                if not math.isclose(line, -away_line, abs_tol=1e-9):
                    raise ValueError('nonopposing_lines')
                target = 0 if margin + line > 0 else 1 if margin + line < 0 else 2
                pushes += target == 2
                for key, values in (('candidate', candidate), ('baseline', baseline)):
                    home = probabilities(row.get(key + '_home'))
                    away = probabilities(row.get(key + '_away'))
                    if any(not math.isclose(a, b, abs_tol=1e-9)
                           for a, b in zip(away, (home[1], home[0], home[2]))):
                        raise ValueError('asymmetric_probabilities')
                    # Complementary away score is identical, not another game.
                    values.append(sum((p - int(i == target)) ** 2 for i, p in enumerate(home)) / 2)
            c, b = mean(candidate), mean(baseline)
            scored.append(dict(canonical_event_id=event, decisions=len(rows),
                               push_decisions=pushes, candidate_brier=c,
                               baseline_brier=b, paired_difference=c-b))
        except (ValueError, TypeError) as exc:
            reason = str(exc)
            if reason not in {'invalid_number', 'invalid_probabilities', 'missing_or_duplicate_outcome',
                              'unverified_settlement', 'invalid_final_score_margin', 'invalid_chronology',
                              'unverified_forecast', 'duplicate_or_missing_decision', 'missing_model_version',
                              'nonopposing_lines', 'asymmetric_probabilities', 'model_version_mismatch'}:
                reason = 'invalid_timestamp'
            rejected[reason] += 1
    return dict(status='descriptive_only' if scored else 'insufficient_data',
                independent_events=len(scored), events=scored, model_versions=list(model_versions),
                missing_forecast_events=sorted(allowed - set(groups)), rejected=dict(rejected),
                mean_paired_brier_difference=mean(r['paired_difference'] for r in scored) if scored else None,
                approved_for_picks=False, model_trained=False,
                limitations=['Negative difference favors candidate; no efficacy conclusion.',
                             'Power, bootstrap CI, calibration and replication not evaluated.',
                             'Caller flags do not prove source verification or immutable persistence.'])
