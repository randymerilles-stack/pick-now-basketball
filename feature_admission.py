"""Offline research features from externally reviewed, paired observations.

The default registry is empty: no current feed/rule configuration is approved.
Registry entries are trusted caller inputs, not verification performed here.
No outcomes are accepted as feature inputs. Never wired to live selections.
"""
import math
from datetime import datetime
from remaining_time import remaining_regulation_seconds
from timing_windows import timing_window


def stamp(value):
    if not isinstance(value, str):
        raise ValueError('invalid_timestamp')
    result = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if result.tzinfo is None:
        raise ValueError('invalid_timestamp')
    return result


def number(value):
    if type(value) not in (float, int) or not math.isfinite(value):
        raise ValueError('invalid_number')
    return value


def admit_features(record, *, evidence_registry=None):
    """Require reviewed provenance, exact state/price agreement and fresh inputs.

    Research timing policy: all four source observations <=30s old, none in
    future; maximum timestamp spread 5s. This policy is not a measured SLA.
    Same-book scope must be full_game_handicap including overtime, with reviewed
    settlement semantics. Overtime observations themselves remain excluded.
    """
    base = dict(approved_for_picks=False, training_eligible=False)
    try:
        if not isinstance(record, dict):
            raise ValueError('invalid_record')
        evidence_id = record.get('evidence_id')
        if not isinstance(evidence_id, str):
            raise ValueError('unreviewed_evidence')
        evidence = (evidence_registry or {}).get(evidence_id)
        if not isinstance(evidence, dict) or evidence.get('reviewed') is not True:
            raise ValueError('unreviewed_evidence')
        required = ('identity', 'clock_semantics', 'league_rules', 'settlement', 'independent_provenance')
        if any(evidence.get(k) is not True for k in required):
            raise ValueError('unreviewed_evidence')
        refs = evidence.get('references')
        if not isinstance(refs, list) or not refs or any(not isinstance(r, str) or not r.strip() for r in refs):
            raise ValueError('missing_evidence_references')
        for key in ('canonical_event_id', 'league', 'bookmaker'):
            if (not isinstance(record.get(key), str) or not record[key].strip()
                    or evidence.get(key) != record[key]):
                raise ValueError('evidence_identity_mismatch')
        decision = stamp(record.get('decision_at'))
        if stamp(evidence.get('reviewed_at')) > decision:
            raise ValueError('evidence_reviewed_after_decision')
        state, other = record['state'], record['independent_state']
        quote, corroboration = record['quote'], record['independent_quote']
        observations = (state, other, quote, corroboration)
        for obs in observations:
            if obs.get('canonical_event_id') != record['canonical_event_id']:
                raise ValueError('observation_identity_mismatch')
            if not isinstance(obs.get('source'), str) or not obs['source'].strip():
                raise ValueError('missing_source')
        if state['source'] == other['source'] or quote['source'] == corroboration['source']:
            raise ValueError('same_acquisition_source')
        if (evidence.get('state_sources') != [state['source'], other['source']] or
                evidence.get('quote_sources') != [quote['source'], corroboration['source']]):
            raise ValueError('unreviewed_acquisition_source')
        times = [stamp(o.get('observed_at')) for o in observations]
        receipts = [stamp(o.get('received_at')) for o in observations]
        if any(not t <= r <= decision for t, r in zip(times, receipts)):
            raise ValueError('invalid_receipt_chronology')
        if any(not 0 <= (decision-t).total_seconds() <= 30 for t in times):
            raise ValueError('stale_or_future_observation')
        if (max(times)-min(times)).total_seconds() > 5:
            raise ValueError('observation_skew')
        state_fields = ('home_score', 'away_score', 'period', 'minutes', 'seconds')
        if any(type(state.get(k)) is not int for k in state_fields):
            raise ValueError('invalid_explicit_state')
        if min(state['home_score'], state['away_score']) < 0:
            raise ValueError('invalid_explicit_state')
        if any(type(other.get(k)) is not int or other[k] != state[k] for k in state_fields):
            raise ValueError('state_disagreement')
        if state.get('overtime') is not False or other.get('overtime') is not False:
            raise ValueError('overtime_or_unknown')
        for q in (quote, corroboration):
            if (q.get('scope') != 'full_game_handicap' or q.get('includes_overtime') is not True
                    or q.get('bookmaker') != record['bookmaker']):
                raise ValueError('market_scope_mismatch')
            for k in ('home_line', 'away_line', 'home_odds', 'away_odds'):
                number(q.get(k))
            if (not math.isclose(q['home_line'], -q['away_line'], abs_tol=1e-9)
                    or min(q['home_odds'], q['away_odds']) <= 1):
                raise ValueError('invalid_quote_pair')
        if any(not math.isclose(quote[k], corroboration[k], abs_tol=1e-9)
               for k in ('home_line', 'away_line', 'home_odds', 'away_odds')):
            raise ValueError('quote_disagreement')
        remaining = remaining_regulation_seconds(state['period'], state['minutes'], state['seconds'],
            regulation_periods=evidence.get('regulation_periods'), period_seconds=evidence.get('period_seconds'),
            clock_direction=evidence.get('clock_direction'), overtime=False,
            clock_semantics_verified=True, league_rules_verified=True, state_alignment_verified=True)
        if remaining is None:
            raise ValueError('invalid_regulation_clock')
        regulation = evidence['regulation_periods'] * evidence['period_seconds']
        home_implied, away_implied = 1/quote['home_odds'], 1/quote['away_odds']
        home_market = home_implied / (home_implied + away_implied)
        margin = state['home_score']-state['away_score']
        sides = {side: dict(score_margin=sign*margin, line=quote[side+'_line'],
                           odds=quote[side+'_odds'], market_probability=p)
                 for side, sign, p in (('home', 1, home_market), ('away', -1, 1-home_market))}
        return dict(base, status='research_features_only', canonical_event_id=record['canonical_event_id'],
                    evidence_id=evidence_id, decision_at=record['decision_at'], period=state['period'],
                    remaining_seconds=remaining, regulation_seconds=regulation,
                    timing_window=timing_window(remaining, regulation, semantics_verified=True), sides=sides)
    except (KeyError, TypeError, ValueError, AttributeError, OverflowError) as exc:
        known = {'invalid_record', 'unreviewed_evidence', 'missing_evidence_references',
                 'evidence_identity_mismatch', 'evidence_reviewed_after_decision',
                 'observation_identity_mismatch', 'missing_source', 'same_acquisition_source',
                 'unreviewed_acquisition_source', 'invalid_receipt_chronology',
                 'stale_or_future_observation', 'observation_skew', 'invalid_explicit_state',
                 'state_disagreement', 'overtime_or_unknown', 'market_scope_mismatch',
                 'invalid_number', 'invalid_quote_pair', 'quote_disagreement', 'invalid_regulation_clock',
                 'invalid_timestamp'}
        return dict(base, status='rejected', reason=str(exc) if str(exc) in known else 'invalid_record')
