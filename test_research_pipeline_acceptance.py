"""Offline composition acceptance. All passing forecasts use synthetic fixtures.

No synthetic row is training evidence or a qualified Priority Pick. The one
real archived capture is used only to verify rejection with no approved registry.
"""
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch
from evaluation_split import plan_splits
from feature_admission import admit_features
from forecast_journal import append_forecast, read_forecast
from forecast_scoring import score_frozen_forecasts
from fixture_uncertainty import fixture_bootstrap
from probability_diagnostics import diagnose_probabilities
from test_feature_admission import fixture


def synthetic_game(index):
    record, registry = fixture()
    event = 'synthetic-g'+str(index)
    observed = datetime(2026,1,index+1,1,0,0,tzinfo=timezone.utc)
    decision = observed+timedelta(seconds=5)
    record.update(canonical_event_id=event, decision_at=decision.isoformat())
    registry['synthetic']['canonical_event_id'] = event
    for key in ('state', 'independent_state', 'quote', 'independent_quote'):
        record[key].update(canonical_event_id=event, observed_at=observed.isoformat(),
                           received_at=(observed+timedelta(seconds=1)).isoformat())
    for key in ('quote','independent_quote'):
        record[key].update(home_line=-3.5, away_line=3.5)
    prediction=dict(decision_id='synthetic-d',candidate_version='synthetic-score-time',
                    baseline_version='synthetic-market',model_frozen_at='2025-12-31T00:00:00Z',
                    candidate_home=[.8,.2,0],candidate_away=[.2,.8,0],
                    baseline_home=[.5,.5,0],baseline_away=[.5,.5,0])
    result=dict(canonical_event_id=event,settlement_verified=True,
                final_home_margin=4 if index%2==0 else 2,
                finished_at=(observed+timedelta(hours=1)).isoformat(),
                available_at=(observed+timedelta(hours=1,minutes=1)).isoformat())
    return record,registry,prediction,result,decision+timedelta(seconds=1)


class PipelineAcceptanceTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.journal=Path(self.temp.name)/'synthetic-research.sqlite'

    def test_admission_journal_locked_split_score_and_diagnostics(self):
        forecasts=[];outcomes=[];split_rows=[]
        for i in range(6):
            record,registry,prediction,outcome,now=synthetic_game(i)
            admission=admit_features(record,evidence_registry=registry)
            self.assertEqual(admission['status'],'research_features_only')
            self.assertFalse(admission['training_eligible'])
            with patch('forecast_journal.utc_now',return_value=now):
                receipt=append_forecast(self.journal,record,prediction,evidence_registry=registry)
            # A JSON round trip represents a separately retained receipt.
            forecasts.append(read_forecast(self.journal,json.loads(json.dumps(receipt))))
            outcomes.append(outcome)
            split_rows.append(dict(canonical_event_id=record['canonical_event_id'],
                decision_at=record['decision_at'],outcome_available_at=outcome['available_at'],
                identity_verified=True,state_verified=True,odds_verified=True))
        splits=plan_splits(split_rows,validation_start='2026-01-03T00:00:00Z',
                           test_start='2026-01-05T00:00:00Z')
        self.assertEqual(splits['event_counts'],dict(development=2,validation=2,test=2))
        versions=('synthetic-score-time','synthetic-market')
        score=score_frozen_forecasts(forecasts,outcomes,test_event_ids=splits['event_ids']['test'],
                                    model_versions=versions)
        self.assertEqual(score['independent_events'],2)
        self.assertEqual(score['rejected'],{'outside_locked_test':4})
        uncertainty=fixture_bootstrap(score)
        diagnostics=diagnose_probabilities(forecasts,outcomes,test_event_ids=splits['event_ids']['test'],
                                           model_versions=versions)
        self.assertAlmostEqual(uncertainty['paired_mean'],.09)
        self.assertEqual(diagnostics['independent_events'],2)
        self.assertEqual(diagnostics['models']['candidate']['log_loss_status'],'finite')
        for report in (splits,score,uncertainty,diagnostics):
            self.assertFalse(report['approved_for_picks'])
            json.dumps(report,allow_nan=False)

    def test_actual_archived_capture_never_auto_admitted(self):
        path=Path(__file__).parent/'espn_odds_feasibility_2026-10-29.json'
        archived=json.loads(path.read_text())
        self.assertEqual(len(archived['events']),12)
        for event in archived['events']:
            self.assertTrue(event['status']['type']['completed'])
            rejected=admit_features(event)
            self.assertEqual(rejected['status'],'rejected')
            self.assertFalse(rejected['training_eligible'])
            with self.assertRaises(ValueError):
                append_forecast(self.journal,event,{})
        self.assertFalse(self.journal.exists())

    def test_conflicting_quarter_stops_before_persistence(self):
        record,registry,prediction,_,now=synthetic_game(0)
        record['independent_state']['period']=2
        self.assertEqual(admit_features(record,evidence_registry=registry)['reason'],'state_disagreement')
        with patch('forecast_journal.utc_now',return_value=now):
            with self.assertRaises(ValueError):
                append_forecast(self.journal,record,prediction,evidence_registry=registry)
        self.assertFalse(self.journal.exists())

    def test_tampered_journal_stops_before_scoring(self):
        record,registry,prediction,_,now=synthetic_game(0)
        with patch('forecast_journal.utc_now',return_value=now):
            receipt=append_forecast(self.journal,record,prediction,evidence_registry=registry)
        with sqlite3.connect(self.journal) as db:
            db.execute("UPDATE forecasts SET payload='{}'")
        with self.assertRaisesRegex(ValueError,'digest mismatch'):
            read_forecast(self.journal,receipt)


if __name__=='__main__':
    unittest.main()
