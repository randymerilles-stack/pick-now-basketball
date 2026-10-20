"""Conservative provider-result labels for research; never approve a pick."""
from datetime import datetime
import math
import re


def timestamp(value):
    if not isinstance(value,str):raise ValueError('Missing timestamp')
    value=datetime.fromisoformat(value.replace('Z','+00:00'))
    if value.tzinfo is None:raise ValueError('Timezone required')
    return value


def join_outcome(observation, decision_at, results, results_received_at):
    """Match one exact event; retain result availability to prevent leakage."""
    output={'fixture_id':observation.get('fixture_id'),'status':'unlabelled',
            'labels':[],'approved_for_picks':False,'independently_verified':False}
    candidates=[r for r in results if isinstance(r,dict)
                and str(r.get('fixture_id'))==str(observation.get('fixture_id'))]
    if len(candidates)!=1:
        output['reason']='missing_or_ambiguous_result';return output
    result=candidates[0]
    if (result.get('sport')!='basketball' or result.get('status')!='finished'
        or any(not observation.get(k) or result.get(k)!=observation[k] for k in ('home','away','league'))):
        output['reason']='event_identity_or_final_status_not_verified';return output
    score=result.get('final_score')
    matched=re.fullmatch(r'(\d+)\s*-\s*(\d+)',score.strip()) if isinstance(score,str) else None
    if not matched:
        output['reason']='malformed_final_score';return output
    home,away=map(int,matched.groups())
    if home==away:
        output['reason']='tied_score_not_accepted_as_final';return output
    try:
        decision=timestamp(decision_at);finished=timestamp(result.get('finished_at'))
        received=timestamp(results_received_at)
        updated=timestamp(result['updated_at']) if result.get('updated_at') is not None else finished
        if not decision<finished<=received or updated>received:raise ValueError('Invalid chronology')
    except (TypeError,ValueError,OverflowError):
        output['reason']='outcome_chronology_unverified';return output
    quotes=observation.get('quotes')
    if not isinstance(quotes,list) or len(quotes)!=2:
        output['reason']='invalid_quote_pair';return output
    by_team={q.get('team'):q for q in quotes if isinstance(q,dict)}
    if set(by_team)!={observation['home'],observation['away']}:
        output['reason']='invalid_quote_pair';return output
    lines=[]
    for team in (observation['home'],observation['away']):
        quote=by_team[team];line=quote.get('line');odds=quote.get('odds')
        if (type(line) not in (int,float) or not math.isfinite(line) or line*2!=int(line*2)
            or type(odds) not in (int,float) or not math.isfinite(odds) or odds<=1):
            output['reason']='invalid_quote_pair';return output
        lines.append(line)
    if lines[0]!=-lines[1]:
        output['reason']='invalid_quote_pair';return output
    for team,line in zip((observation['home'],observation['away']),lines):
        margin=(home-away if team==observation['home'] else away-home)+line
        output['labels'].append({'team':team,'line':line,'cover_result':'win' if margin>0 else 'loss' if margin<0 else 'push',
                                 'covered':int(margin>0) if margin!=0 else None})
    output.update(status='provider_labelled_research_only',final_score=score,
                  decision_at=decision.isoformat(),finished_at=finished.isoformat(),
                  outcome_available_at=max(finished,updated,received).isoformat(),
                  training_eligible=False,
                  reason='Provider outcome only; score/time features and independent settlement still unverified.')
    return output
