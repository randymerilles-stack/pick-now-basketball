"""Audit declared event-time coverage without backdating data availability."""
from datetime import datetime


def stamp(value):
    if not isinstance(value,str):raise ValueError('Missing timestamp')
    result=datetime.fromisoformat(value.replace('Z','+00:00'))
    if result.tzinfo is None:raise ValueError('Timezone required')
    return result


def audit_play_timestamps(summary, expected_event_id, received_at):
    received=stamp(received_at)
    plays=summary.get('plays',[])
    if not isinstance(plays,list):plays=[]
    identity=bool(isinstance(expected_event_id,str) and expected_event_id
                  and summary.get('header',{}).get('id')==expected_event_id)
    times=[];missing=0;invalid=0;future=0;backward=0
    for play in plays:
        if not isinstance(play,dict) or play.get('wallclock') is None:
            missing+=1;continue
        try:ts=stamp(play['wallclock'])
        except (ValueError,TypeError):invalid+=1;continue
        if ts>received:future+=1;continue
        if times and ts<times[-1]:backward+=1
        times.append(ts)
    declared=summary.get('wallclockAvailable') is True
    return {'event_id':expected_event_id,'identity_matches':identity,
            'wallclock_declared':declared,'play_count':len(plays),
            'valid_timestamp_count':len(times),'missing_timestamp_count':missing,
            'invalid_timestamp_count':invalid,'future_timestamp_count':future,
            'backward_timestamp_transitions':backward,
            'first_valid_wallclock':times[0].isoformat() if times else None,
            'last_valid_wallclock':times[-1].isoformat() if times else None,
            'complete_ordered_timestamp_coverage':bool(identity and declared and plays
                and len(times)==len(plays) and backward==0),
            'data_available_no_earlier_than':received.isoformat(),
            'training_eligible':False,'approved_for_picks':False}
