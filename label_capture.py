"""Bounded provider-result joining for a persisted capture file."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import urlencode
from outcome_join import join_outcome


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('capture',type=Path)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    data=json.loads(args.capture.read_text())
    captures=data.get('captures',[data])
    ids=sorted({str(o['fixture_id']) for c in captures for o in c.get('observations',[])})
    if len(ids)>20:raise ValueError('Use a bounded capture with at most 20 fixtures')
    fetched={}
    for fixture_id in ids:
        url='https://moviodds.com/results?'+urlencode({'sport':'basketball','fi':fixture_id})
        try:
            with urlopen(Request(url,headers={'User-Agent':'PickNowOutcomeAudit/0.1'}),timeout=20) as response:
                raw=response.read(3_000_001)
                if len(raw)>3_000_000:raise ValueError('Oversized result')
                result=json.loads(raw)
            fetched[fixture_id]={'source':url,'received_at':datetime.now(timezone.utc).isoformat(),
                                 'response':result}
        except Exception as error:
            fetched[fixture_id]={'source':url,'received_at':datetime.now(timezone.utc).isoformat(),
                                 'error_type':type(error).__name__,'response':{'results':[]}}
    joined=[]
    for capture in captures:
        for observation in capture.get('observations',[]):
            result=fetched[str(observation['fixture_id'])]
            label=join_outcome(observation,capture['received_at'],result['response'].get('results',[]),result['received_at'])
            label['market_id']=observation.get('market_id')
            joined.append(label)
    report={'schema_version':1,'input_capture':args.capture.name,'results':fetched,'joined':joined,
            'unique_fixtures':len(ids),'observation_rows':len(joined),
            'labelled_rows':sum(r['status']=='provider_labelled_research_only' for r in joined),
            'approved_for_picks':False,'training_eligible':False,
            'limitations':['Repeated observations and opposing sides are not independent games.',
                          'No model forecasts were evaluated; these outcomes are not a win-rate claim.',
                          'Provider settlement and score/time feature semantics remain independently unverified.']}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('x',encoding='utf-8') as output:json.dump(report,output,indent=2,allow_nan=False)
    print(json.dumps({k:report[k] for k in ('unique_fixtures','observation_rows','labelled_rows','training_eligible','approved_for_picks')}))


if __name__=='__main__':main()
