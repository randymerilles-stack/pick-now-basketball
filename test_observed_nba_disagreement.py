"""Regression evidence from real captures, not fabricated training samples."""
import json
from pathlib import Path
import unittest


class ObservedDisagreementTests(unittest.TestCase):
    def test_matching_score_does_not_imply_matching_period(self):
        capture = json.loads((Path(__file__).parent / 'nba_late_alignment_2026-10-24T1043.json').read_text())
        by_id = {r['provider_fixture']['id']: r for r in capture['candidate_pairs']}
        for fid in ('203335721', '203335731'):
            row = by_id[fid]
            provider = row['provider_fixture']
            event = row['scoreboard_event']
            scores = {t['homeAway']: t['score'] for t in event['competitions'][0]['competitors']}
            self.assertEqual(provider['score'], scores['home'] + '-' + scores['away'])
            self.assertNotEqual(provider['stats']['period'], event['status']['period'])
            self.assertFalse(row['diagnostics']['period_matches'])
        self.assertFalse(capture['training_eligible'])
        self.assertFalse(capture['approved_for_picks'])
